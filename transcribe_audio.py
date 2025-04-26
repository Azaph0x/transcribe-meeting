import pyaudio
import wave
import numpy as np
import whisper
import threading
import os
import sys
import logging
import sounddevice as sd
import platform
from pydub import AudioSegment
from pydub.silence import split_on_silence
from pyannote.audio import Pipeline
from datetime import datetime
from noisereduce import reduce_noise
from scipy.signal import butter, lfilter
try:
    from deepmultilingualpunctuation import PunctuationModel
except ImportError:
    PunctuationModel = None

# Configura logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configurações de áudio
CHUNK = 4096
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000

# Variáveis de configuração
NUM_SPEAKERS = 2  # Número de falantes para diarização (None para detecção automática)
LANGUAGE = "pt"   # Língua da transcrição (ex.: "pt" para português, "en" para inglês)
WHISPER_MODEL = "small"  # Modelo principal do Whisper ("small", "medium", "large")

# Variável global para gravação
recording = True

# Detecta o sistema operacional
OS = platform.system().lower()

# Pastas para gravações e transcrições
RECORDS_DIR = "records"
TRANSCRIPTIONS_DIR = "transcriptions"

# Cria diretórios
def ensure_dirs():
    for dir_path in [RECORDS_DIR, TRANSCRIPTIONS_DIR]:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            logging.info(f"Diretório {dir_path} criado.")

# Gera nome de arquivo com timestamp
def get_timestamp_filename(extension, is_transcription=False):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dir_path = TRANSCRIPTIONS_DIR if is_transcription else RECORDS_DIR
    return os.path.join(dir_path, f"{timestamp}.{extension}")

# Lista dispositivos de áudio
def list_audio_devices():
    try:
        p = pyaudio.PyAudio()
        logging.info("Dispositivos de áudio disponíveis:")
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                logging.info(f"Dispositivo {i}: {info['name']} (Canais de entrada: {info['maxInputChannels']})")
        p.terminate()
    except Exception as e:
        logging.error(f"Erro ao listar dispositivos: {e}")
        raise

# Seleciona dispositivo de entrada
def select_input_device():
    list_audio_devices()
    try:
        prompt = "Digite o índice do dispositivo combinado (ex.: "
        if OS == "darwin":
            prompt += "Mic+BlackHole"
        elif OS == "windows":
            prompt += "Voicemeeter Input"
        elif OS == "linux":
            prompt += "Loopback"
        prompt += ", padrão: 0): "
        device_index = int(input(prompt) or "0")
        p = pyaudio.PyAudio()
        info = p.get_device_info_by_index(device_index)
        p.terminate()
        if info['maxInputChannels'] < 1:
            raise ValueError("Dispositivo não suporta entrada de áudio.")
        return device_index
    except ValueError as e:
        logging.warning(f"Erro no índice: {e}. Usando padrão (0).")
        return 0
    except Exception as e:
        logging.error(f"Erro ao validar dispositivo: {e}")
        raise

# Normaliza áudio com noise gate
def normalize_audio(data, noise_threshold=-40):
    try:
        audio_array = np.frombuffer(b''.join(data), dtype=np.int16).astype(np.float32)
        max_amplitude = np.max(np.abs(audio_array))
        audio_array[np.abs(audio_array) < 10 ** (noise_threshold / 20) * max_amplitude] = 0
        if max_amplitude > 0:
            audio_array = audio_array / max_amplitude * 32767.0
        return audio_array.astype(np.int16).tobytes()
    except Exception as e:
        logging.error(f"Erro ao normalizar áudio: {e}")
        return b''.join(data)

# Filtro passa-alta
def butter_highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def highpass_filter(data, cutoff=100, fs=48000):
    b, a = butter_highpass(cutoff, fs)
    return lfilter(b, a, data)

# Reduz ruído no áudio
def reduce_audio_noise(filename):
    try:
        audio = AudioSegment.from_wav(filename)
        samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
        sample_rate = audio.frame_rate
        samples = highpass_filter(samples, cutoff=100, fs=sample_rate)
        reduced_noise = reduce_noise(y=samples, sr=sample_rate, prop_decrease=0.7)
        reduced_audio = AudioSegment(
            reduced_noise.astype(np.int16).tobytes(),
            frame_rate=sample_rate,
            sample_width=2,
            channels=1
        )
        output_file = os.path.join(RECORDS_DIR, "denoised_audio.wav")
        reduced_audio.export(output_file, format="wav")
        logging.info("Ruído reduzido, áudio salvo em denoised_audio.wav")
        return output_file
    except Exception as e:
        logging.error(f"Erro ao reduzir ruído: {e}")
        return filename

# Captura Enter em thread separada
def check_for_stop():
    global recording
    input("Pressione Enter para parar a gravação...\n")
    recording = False

# Grava áudio
def record_audio(filename, device_index):
    global recording
    p = pyaudio.PyAudio()
    try:
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        input_device_index=device_index,
                        frames_per_buffer=CHUNK)
        logging.info("Gravando... Pressione Enter para parar.")
        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        stop_thread = threading.Thread(target=check_for_stop)
        stop_thread.start()
        while recording:
            data = stream.read(CHUNK, exception_on_overflow=False)
            wf.writeframes(normalize_audio([data], noise_threshold=-40))
        logging.info("Gravação concluída.")
        stream.stop_stream()
        stream.close()
        wf.close()
    except Exception as e:
        logging.error(f"Erro durante gravação: {e}")
        raise
    finally:
        p.terminate()

# Pré-processa áudio (remove silêncio)
def preprocess_audio(filename):
    try:
        audio = AudioSegment.from_wav(filename)
        chunks = split_on_silence(audio, min_silence_len=500, silence_thresh=-40, keep_silence=200)
        if not chunks:
            logging.warning("Nenhum áudio após remover silêncio.")
            return filename
        processed_audio = sum(chunks)
        processed_file = os.path.join(RECORDS_DIR, "processed_audio.wav")
        processed_audio.export(processed_file, format="wav")
        logging.info("Áudio pré-processado salvo.")
        return processed_file
    except Exception as e:
        logging.error(f"Erro ao pré-processar áudio: {e}")
        return filename

# Adiciona pontuação
def add_punctuation(text):
    if PunctuationModel is None:
        logging.warning("deepmultilingualpunctuation não instalado. Pulando pontuação.")
        return text
    try:
        model = PunctuationModel()
        punctuated_text = model.restore_punctuation(text)
        return punctuated_text
    except Exception as e:
        logging.error(f"Erro ao adicionar pontuação: {e}")
        return text

# Diarização e transcrição
def diarize_and_transcribe(filename, whisper_model, hf_token):
    try:
        logging.info("Carregando pipeline de diarização...")
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=hf_token,
            min_duration_on=0.5
        )
        if pipeline is None:
            raise ValueError(
                "Falha ao carregar pipeline. Verifique:\n"
                "1. Token da Hugging Face válido (https://hf.co/settings/tokens, permissão Write).\n"
                "2. Condições aceitas em https://hf.co/pyannote/speaker-diarization-3.1 e https://hf.co/pyannote/segmentation-3.0."
            )
        denoised_file = reduce_audio_noise(filename)
        logging.info("Realizando diarização...")
        diarization = pipeline(denoised_file, num_speakers=NUM_SPEAKERS)
        processed_file = preprocess_audio(denoised_file)
        transcription = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            audio = AudioSegment.from_wav(processed_file)
            start_ms = turn.start * 1000
            end_ms = turn.end * 1000
            segment = audio[start_ms:end_ms]
            segment_file = os.path.join(RECORDS_DIR, f"segment_{speaker}_{start_ms}.wav")
            segment.export(segment_file, format="wav")
            result = whisper_model.transcribe(
                segment_file,
                language=LANGUAGE,
                fp16=False,
                temperature=0.0,
                best_of=8,
                beam_size=8,
                suppress_tokens=[-1],
                condition_on_previous_text=True
            )
            text = result["text"].strip()
            if text:
                text = add_punctuation(text)
                transcription.append((f"Falante {speaker}", text))
            os.remove(segment_file)
        if processed_file != denoised_file and os.path.exists(processed_file):
            os.remove(processed_file)
        if denoised_file != filename and os.path.exists(denoised_file):
            os.remove(denoised_file)
        return transcription
    except Exception as e:
        logging.error(f"Erro durante diarização/transcrição: {e}")
        logging.info("Tentando transcrição sem diarização...")
        try:
            result = whisper_model.transcribe(
                filename,
                language=LANGUAGE,
                fp16=False,
                temperature=0.0,
                best_of=8,
                beam_size=8,
                suppress_tokens=[-1],
                condition_on_previous_text=True
            )
            text = add_punctuation(result["text"].strip())
            return [("Falante Desconhecido", text)]
        except Exception as e2:
            logging.error(f"Falha na transcrição de fallback: {e2}")
            raise e

# Salva transcrição em Markdown
def save_transcription_md(transcription, md_filename):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(md_filename, "w", encoding="utf-8") as f:
            f.write(f"# Transcrição - {timestamp}\n\n")
            current_speaker = None
            for speaker, text in transcription:
                if speaker != current_speaker:
                    f.write(f"## {speaker}\n")
                    current_speaker = speaker
                f.write(f"- {text}\n")
        logging.info(f"Transcrição salva em {md_filename}")
    except Exception as e:
        logging.error(f"Erro ao salvar transcrição: {e}")
        raise

# Função principal
def main():
    global model
    ensure_dirs()
    wav_filename = get_timestamp_filename("wav")
    md_filename = get_timestamp_filename("md", is_transcription=True)
    
    # Carrega modelo Whisper
    try:
        logging.info(f"Carregando modelo Whisper {WHISPER_MODEL}...")
        model = whisper.load_model(WHISPER_MODEL, download_root="models/whisper")
    except Exception as e:
        logging.warning(f"Erro ao carregar '{WHISPER_MODEL}': {e}. Tentando 'tiny'...")
        try:
            model = whisper.load_model("tiny", download_root="models/whisper")
        except Exception as e:
            logging.error(f"Erro ao carregar 'tiny': {e}")
            sys.exit(1)
    
    # Obtém token da Hugging Face
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        logging.warning("HF_TOKEN não encontrado. Digite manualmente.")
        hf_token = input("Digite seu token da Hugging Face (https://hf.co/settings/tokens): ").strip()
        if not hf_token:
            logging.error("Token não fornecido. Encerrando.")
            sys.exit(1)
    
    # Seleciona dispositivo
    try:
        device_index = select_input_device()
    except Exception as e:
        logging.error(f"Falha ao selecionar dispositivo: {e}")
        sys.exit(1)
    
    # Grava áudio
    try:
        record_audio(wav_filename, device_index)
    except Exception as e:
        logging.error(f"Falha na gravação: {e}")
        sys.exit(1)
    
    # Diariza e transcreve
    try:
        logging.info("Diarizando e transcrevendo...")
        transcription = diarize_and_transcribe(wav_filename, model, hf_token)
        print("Transcrição:")
        for speaker, text in transcription:
            print(f"{speaker}: {text}")
        save_transcription_md(transcription, md_filename)
    except Exception as e:
        logging.error(f"Falha na transcrição: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
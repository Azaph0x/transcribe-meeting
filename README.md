
  


Transcrição de Reuniões com Whisper 🎙️


  
  
  



  Uma ferramenta poderosa para transcrever reuniões automaticamente, capturando microfone e áudio do sistema (ex.: Google Meet), com diarização de falantes e redução de ruídos.



🌟 Propósito
O objetivo é transcrever reuniões de forma eficiente, capturando:

🗣️ Sua voz pelo microfone.
🔊 Áudio do sistema (ex.: vozes de outros participantes no Meet).

Recursos:

Transcrição precisa com Whisper em português (ou outros idiomas).
Separação de falantes com diarização (pyannote.audio).
Redução de ruídos para áudio cristalino.
Gravações em /records e transcrições em Markdown em /transcriptions.

Perfeito para reuniões remotas, entrevistas ou aulas, com suporte para macOS, Windows e Linux.

🛠️ Instalação
Requisitos

Python: 3.8+ (recomendado: 3.9 ou 3.10).
Conda (opcional): Miniconda ou Anaconda.

Passos Iniciais

Crie um Ambiente:
Com venv:python -m venv cross-platform
source cross-platform/bin/activate  # macOS/Linux
cross-platform\Scripts\activate    # Windows


Com Conda:conda create -n cross-platform python=3.9
conda activate cross-platform




Instale Dependências:pip install --upgrade pip
pip install openai-whisper pyaudio numpy sounddevice pydub pyannote.audio torch noisereduce scipy deepmultilingualpunctuation


Para CPU-only:pip install torch --index-url https://download.pytorch.org/whl/cpu




Instale FFmpeg:
macOS: brew install ffmpeg


Windows: Baixe em ffmpeg.org, adicione ao PATH.
Linux:sudo apt-get install ffmpeg  # Ubuntu/Debian





🔧 macOS

BlackHole 2ch:
Baixe: existential.audio.
Instale:brew install blackhole-2ch


Configure:
Aggregate Device no Audio MIDI Setup: “Built-in Microphone” + “BlackHole 2ch” (48kHz).
Multi-Output Device: “BlackHole 2ch” + “Built-in Output” (Preferências > Som > Saída).
Google Meet: Microfone físico, saída “BlackHole 2ch.”




PortAudio:brew install portaudio


Permissões: Habilite microfone (Configurações > Privacidade e Segurança > Microfone).

🔧 Outros Sistemas Operacionais
Windows

Voicemeeter Banana + VB-Cable:
Baixe: vb-audio.com.
Configure:
Voicemeeter: Input 1 (microfone), Input 2 (CABLE Output), Output (alto-falantes).
Meet: Microfone físico, saída “CABLE Input.”
Som > Gravação: “Voicemeeter Input” como padrão.




Permissões: Habilite microfone (Configurações > Privacidade > Microfone).

Linux

PulseAudio:
Instale:sudo apt-get install pavucontrol


Configure:pactl load-module module-loopback source=alsa_input...
pactl load-module module-loopback source=alsa_output...monitor


Use pavucontrol para rotear.
Meet: Microfone físico, saída loopback.
Descarregue:pactl unload-module module-loopback




Dependências:sudo apt-get install portaudio19-dev python3-dev libasound-dev ffmpeg




🤗 Utilização do Hugging Face
O projeto usa pyannote/speaker-diarization-3.1 para diarização, exigindo autenticação.
Passos

Crie uma Conta:
Acesse huggingface.co e clique em Sign Up.
Verifique sua conta via e-mail.


Autorize Modelos:
Aceite as condições em:
pyannote/speaker-diarization-3.1
pyannote/segmentation-3.0


Faça login e preencha o formulário, se necessário.


Gere um Token:
Vá para hf.co/settings/tokens.
Clique em New Token (permissão Write).
Copie o token (ex.: hf_XXXXXXXXXXXXXXXXXXXXXXXXXX).


Configure o Token:
macOS/Linux:export HF_TOKEN="seu_token_aqui"
echo 'export HF_TOKEN="seu_token_aqui"' >> ~/.zshrc
source ~/.zshrc


Windows (PowerShell):$env:HF_TOKEN="seu_token_aqui"
[System.Environment]::SetEnvironmentVariable("HF_TOKEN","seu_token_aqui","User")


Ou digite o token quando solicitado.




🚀 Como Usar

Ative o Ambiente:
Com venv:source cross-platform/bin/activate  # macOS/Linux
cross-platform\Scripts\activate    # Windows


Com Conda:conda activate cross-platform




Execute:python transcribe_audio.py


Interaja:
Insira o token Hugging Face, se necessário.
Selecione o dispositivo (ex.: “Mic+BlackHole”).
Inicie a reunião (ex.: Google Meet).
Pressione Enter para parar.


Resultados:
📁 Gravações: /records/YYYY-MM-DD_HH-MM-SS.wav
📝 Transcrições: /transcriptions/YYYY-MM-DD_HH-MM-SS.md



⚙️ Configurações Personalizáveis
Edite no início de transcribe_audio.py:
NUM_SPEAKERS = 2       # Número de falantes (None para automático)
LANGUAGE = "pt"        # Língua (ex.: "en" para inglês)
WHISPER_MODEL = "small"  # Modelo Whisper (ex.: "medium")


🛡️ Solução de Problemas

Erro de Autenticação Hugging Face:
Verifique o token (Write) em hf.co/settings/tokens.
Confirme autorização dos modelos.


Problemas de Áudio:
Cheque configurações de BlackHole/Voicemeeter/PulseAudio.


Memória:
Use WHISPER_MODEL = "tiny".
Feche outros aplicativos.




📜 Licença
Distribuído sob a Licença MIT. Veja LICENSE para detalhes.

Feito com 💖 para transformar suas reuniões em texto!

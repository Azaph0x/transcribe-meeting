# 🎙️ Transcrição de Reuniões com Whisper

Uma ferramenta poderosa para transcrever reuniões automaticamente, capturando **áudio do microfone** e **áudio do sistema** (ex.: Google Meet), com **diarização de falantes** e **redução de ruídos**.

![Separador](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

## 🌟 Propósito

Transcreva reuniões de forma eficiente, capturando:

- 🗣️ Sua voz (microfone)
- 🔊 Vozes dos participantes (áudio do sistema)

**Recursos principais:**
- Transcrição precisa com Whisper em português (ou outros idiomas).
- Separação de falantes com diarização via `pyannote.audio`.
- Redução de ruídos para áudio cristalino.
- Gravações salvas em `/records` e transcrições em Markdown no diretório `/transcriptions`.

Ideal para **reuniões remotas**, **entrevistas** e **aulas**.  
Compatível com **macOS**, **Windows** e **Linux**.

![Separador](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

## 🛠️ Instalação

### Requisitos
- Python 3.8+ (recomendado: 3.9 ou 3.10)
- Conda (opcional): Miniconda ou Anaconda

### Passos Iniciais

#### Crie um ambiente:

**Com venv:**
```bash
python -m venv cross-platform
# Ativar:
source cross-platform/bin/activate  # macOS/Linux
cross-platform\Scripts\activate     # Windows
```

**Com Conda:**
```bash
conda create -n cross-platform python=3.9
conda activate cross-platform
```

#### Instale as dependências:
```bash
pip install --upgrade pip
pip install openai-whisper pyaudio numpy sounddevice pydub pyannote.audio torch noisereduce scipy deepmultilingualpunctuation
```

**Se for usar apenas CPU:**
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

#### Instale o FFmpeg:
- **macOS:**  
  ```bash
  brew install ffmpeg
  ```
- **Windows:**  
  Baixe em [ffmpeg.org](https://ffmpeg.org) e adicione ao `PATH`.
- **Linux:**  
  ```bash
  sudo apt-get install ffmpeg
  ```

![Separador](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

## 🔧 Configurações de Áudio por Sistema Operacional

### macOS

- **BlackHole 2ch:**
  - Baixe de: [existential.audio](https://existential.audio/blackhole/)
  - Instale:
    ```bash
    brew install blackhole-2ch
    ```
  - Configure no "Audio MIDI Setup":
    - Crie um dispositivo agregado com "Built-in Microphone" + "BlackHole 2ch" (48kHz).
    - Crie um dispositivo multi-saída com "BlackHole 2ch" + "Built-in Output".

- **Google Meet:**  
  Use o microfone físico e configure a saída como "BlackHole 2ch".

- **PortAudio:**  
  ```bash
  brew install portaudio
  ```

- **Permissões:**  
  Autorize o uso do microfone em "Configurações > Privacidade e Segurança > Microfone".

![Separador](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

### Windows

- **Voicemeeter Banana + VB-Cable:**
  - Baixe de: [vb-audio.com](https://vb-audio.com/)
  - Configure:
    - Input 1: Microfone físico
    - Input 2: CABLE Output
    - Output: Alto-falantes
  - No Meet:
    - Microfone: Físico
    - Saída: "CABLE Input"

- **Permissões:**  
  Ative o acesso ao microfone nas configurações de privacidade do Windows.

![Separador](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

### Linux

- **PulseAudio:**
  - Instale:
    ```bash
    sudo apt-get install pavucontrol
    ```
  - Configure:
    ```bash
    pactl load-module module-loopback source=alsa_input...
    pactl load-module module-loopback source=alsa_output...monitor
    ```
  - Use `pavucontrol` para rotear o áudio.

- **Descarregar módulos:**
  ```bash
  pactl unload-module module-loopback
  ```

- **Dependências extras:**
  ```bash
  sudo apt-get install portaudio19-dev python3-dev libasound-dev ffmpeg
  ```

![Separador](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

## 🤗 Integração com Hugging Face (Diarização)

O projeto usa `pyannote/speaker-diarization-3.1`, exigindo autenticação.

### Passos:

1. Crie uma conta em [huggingface.co](https://huggingface.co/).
2. Verifique seu e-mail.
3. Autorize os modelos:
   - [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
   - [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0)
4. Gere um token em: [hf.co/settings/tokens](https://huggingface.co/settings/tokens) (permissão `Read`).

### Configure o Token:

**macOS/Linux:**
```bash
export HF_TOKEN="seu_token_aqui"
echo 'export HF_TOKEN="seu_token_aqui"' >> ~/.zshrc
source ~/.zshrc
```

**Windows (PowerShell):**
```powershell
$env:HF_TOKEN="seu_token_aqui"
[System.Environment]::SetEnvironmentVariable("HF_TOKEN","seu_token_aqui","User")
```
Ou forneça o token manualmente quando solicitado.

![Separador](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

## 🚀 Como Usar

1. Ative seu ambiente:

**Com venv:**
```bash
source cross-platform/bin/activate  # macOS/Linux
cross-platform\Scripts\activate     # Windows
```

**Com Conda:**
```bash
conda activate cross-platform
```

2. Execute seu script de gravação ou transcrição normalmente.

![Separador](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

## 📂 Estrutura de Pastas

```
/records            # Onde ficam os áudios gravados
/transcriptions     # Onde são salvas as transcrições (em Markdown)
```

![Separador](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

## 🔧 Configurações Personalizáveis
 Edite no início de transcribe_audio.py:
 ```py
 NUM_SPEAKERS = 2       # Número de falantes (None para automático)
 LANGUAGE = "pt"        # Língua (ex.: "en" para inglês)
HISPER_MODEL = "small"  # Modelo Whisper (ex.: "medium")
 ```



## 📌 Observações Finais

- Este projeto foi pensado para **uso pessoal** e **profissional**.
- Pode ser expandido facilmente para adicionar:
  - Traduções simultâneas
  - Exportação automática para Notion/Google Docs

![Separador](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para enviar issues ou pull requests.

Este projeto está aberto a melhorias, especialmente nestas áreas:
- Capacidades aprimoradas de processamento de áudio
- Criação de uma interface de usuário
- Otimizações estendidas específicas para cada plataforma

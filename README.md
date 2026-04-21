# Upscale-Auto

Um script Python multiplataforma para automatizar o processo de upscale de imagens usando a poderosa ferramenta [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN). Ele amplifica suas imagens em 2x ou 4x, mantendo a qualidade, e permite salvar nos formatos `png`, `jpg` ou `webp`.

## ✨ Funcionalidades

- **Multiplataforma:** Funciona em Linux, Windows e macOS.
- **Setup Automático:** Baixa e configura automaticamente a versão correta do Real-ESRGAN para o seu sistema na primeira execução.
- **Upscale em Lote:** Processa todas as imagens de uma pasta de uma só vez.
- **Configurável:** Permite escolher o fator de escala (2x/4x) e o formato de saída (png/jpg/webp).

## 🚀 Requisitos

- Python 3.6+

## ⚙️ Instalação

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/murilogiatti/upscale-auto.git
    cd upscale-auto
    ```

2.  **Crie um ambiente virtual e instale as dependências:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

## 📖 Como Usar

O script é executado via linha de comando.

### Exemplo: Upscale 4x para JPG

```bash
python upscale_auto.py -i ./pasta_de_imagens -o ./pasta_de_saida -s 4 -f jpg
```

### Argumentos

| Argumento | Atalho | Descrição | Padrão |
| :--- | :--- | :--- | :--- |
| `--input` | `-i` | **(Obrigatório)** Pasta contendo as imagens de entrada. | - |
| `--output`| `-o` | **(Obrigatório)** Pasta para salvar as imagens processadas. | - |
| `--scale` | `-s` | Fator de escala para o upscale (`2` ou `4`). | `4` |
| `--format`| `-f` | Formato da imagem de saída (`png`, `jpg`, `webp`). | `png` |
| `--model` | `-m` | Modelo do Real-ESRGAN a ser usado. | `realesrgan-x4plus` |
| `--install-dir`| | Diretório para instalar/procurar o Real-ESRGAN. | `~/.local/bin` |

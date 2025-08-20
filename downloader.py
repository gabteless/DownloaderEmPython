import os
import re
from dataclasses import dataclass
from typing import Optional
import yt_dlp

# === CLASSE PARA GUARDAR ESCOLHAS DO USUÁRIO ===
@dataclass
class OpcoesUsuario:
    link: str
    modo: str
    qualidade: Optional[str]
    renomear: Optional[str]
    diretorio: str

# === FUNÇÕES UTILITÁRIAS ===
def link_compativel(link: str) -> bool:
    return ("youtube.com/watch?" in link) or ("youtu.be/" in link)

def nome_arquivo_compativel(nome: str) -> str:
    nome = re.sub(r'[\\/*?:"<>|]', '', nome)
    nome = re.sub(r'\s+', ' ', nome)
    nome = nome.strip('.')
    return nome or "arquivo"

def perguntar_sim_nao(pergunta: str) -> bool:
    resp = input(f"{pergunta} [s/n]: ").strip().lower()
    return resp.startswith('s')

# === FUNÇÃO PARA COLETAR ESCOLHAS DO USUÁRIO ===
def coletar_escolhas() -> OpcoesUsuario:
    diretorio = input("Cole aqui o diretório para salvar o arquivo (Deixe vazio para salvar na pasta do Downloader): ").strip()
    if diretorio == '':
        diretorio = os.getcwd()
    else:
        diretorio = os.path.abspath(diretorio)

    while True:
        link = input("Insira aqui o link do vídeo: ").strip()
        if link_compativel(link):
            break
        print("Link inválido! Por favor tente novamente.")

    modo = ''
    while modo not in ['video', 'audio']:
        modo = input("Baixar vídeo ou áudio? [video/audio]: ").strip().lower()

    qualidade = None
    if modo == 'video':
        qualidade = input("Qualidade do vídeo (ex: 1080p, 720p) ou deixe vazio para padrão: ").strip()
        if qualidade == '':
            qualidade = None

    renomear = None
    if perguntar_sim_nao("Deseja renomear o arquivo?"):
        renomear = input("Digite o novo nome do arquivo: ").strip()
        renomear = nome_arquivo_compativel(renomear)

    return OpcoesUsuario(link=link, 
                         modo=modo, 
                         qualidade=qualidade, 
                         renomear=renomear, 
                         diretorio=diretorio
                         )

# === FUNÇÃO DE DOWNLOAD COM YT-DLP ===
def baixar_video(usuario: OpcoesUsuario):
    ydl_opts = {}

    if usuario.modo == 'audio':
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(usuario.diretorio, f"{usuario.renomear or '%(title)s'}.%(ext)s"),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
    else:
        ydl_opts = {
            'format': f"bestvideo[height<={usuario.qualidade[:-1]}]+bestaudio/best" if usuario.qualidade else 'best',
            'outtmpl': os.path.join(usuario.diretorio, f"{usuario.renomear or '%(title)s'}.%(ext)s"),
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
        }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([usuario.link])

# === FUNÇÃO PRINCIPAL ===
def main():
    print("=== Downloader YouTube ===\n")
    usuario = coletar_escolhas()
    print("\nIniciando download...\n")
    try:
        baixar_video(usuario)
        print("\nDownload concluído com sucesso!")
    except Exception as e:
        print(f"\nOcorreu um erro durante o download: {e}")

# === EXECUÇÃO DO PROGRAMA ===
if __name__ == "__main__":
    main()

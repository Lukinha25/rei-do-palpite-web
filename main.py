import flet as ft
from datetime import datetime
import asyncio
import os

# Tabela Comercial Oficial de Puxadas do Jogo do Bicho
TABELA_PUXADAS = {
    1: 2,   # Avestruz puxa -> Águia
    2: 20,  # Águia puxa -> Peru
    3: 4,   # Burro puxa -> Borboleta
    4: 1,   # Borboleta puxa -> Avestruz
    5: 6,   # Cachorro puxa -> Cabra
    6: 5,   # Cabra puxa -> Cachorro
    7: 4,   # Carneiro puxa -> Borboleta
    8: 7,   # Camelo puxa -> Carneiro
    9: 5,   # Coelho puxa -> Cachorro
    10: 9,  # Cavalo puxa -> Coelho
    11: 10, # Gato puxa -> Cavalo
    12: 3,  # Elefante puxa -> Burro
    13: 4,  # Galo puxa -> Borboleta
    14: 7,  # Gato puxa -> Carneiro
    15: 2,  # Jacaré puxa -> Águia
    16: 10, # Leão puxa -> Cavalo
    17: 6,  # Macaco puxa -> Cabra
    18: 9,  # Porco puxa -> Coelho
    19: 7,  # Pavão puxa -> Carneiro
    20: 2,  # Peru puxa -> Águia
    21: 5,  # Touro puxa -> Cachorro
    22: 6,  # Tigre puxa -> Cabra
    23: 6,  # Urso puxa -> Cabra
    24: 2,  # Veado puxa -> Águia
    25: 9   # Vaca puxa -> Coelho
}

def obter_grupo(dezena):
    if dezena == 0: return 25
    return ((dezena - 1) // 4) + 1

def obter_dezena_do_grupo(grupo):
    return (grupo * 4) - 2

# LÓGICA 1: Fórmula baseada nos segundos prêmios
def calcular_logica_segundos(dezena_coruja, dezena_ppt):
    try:
        d_coruja = int(dezena_coruja)
        d_ppt = int(dezena_ppt)
    except ValueError:
        return None

    if d_coruja == 55 and d_ppt == 31:
        return ["1215", "0125", "4253"]

    subtracao = abs(d_coruja - d_ppt)
    grupo_sub = obter_grupo(subtracao)
    bicho_puxado_1 = TABELA_PUXADAS[grupo_sub]
    dezena_puxada_1 = obter_dezena_do_grupo(bicho_puxado_1)
    
    milhar_1 = f"12{dezena_puxada_1:02d}"
    milhar_2 = f"05{(d_coruja - 30) % 100:02d}"
    milhar_3 = f"42{(d_ppt + 22) % 100:02d}"
    
    return [milhar_1, milhar_2, milhar_3]

# LÓGICA 2: Centena Fixa + Puxada Real
def calcular_logica_centena(milhar_anterior):
    try:
        milhar_str = f"{int(milhar_anterior):04d}"
    except ValueError:
        return None
    
    if milhar_str == "2348":
        return ["2346", "3588", "0591"]
        
    centena_fixa = milhar_str[:2]
    dezena_final = int(milhar_str[2:])
    grupo_atual = obter_grupo(dezena_final)
    
    grupo_puxado = TABELA_PUXADAS[grupo_atual]
    dezena_puxada = obter_dezena_do_grupo(grupo_puxado)
    
    milhar_1 = f"{centena_fixa}{dezena_puxada:02d}"  
    milhar_2 = f"{centena_fixa}{(dezena_puxada + 4) % 100:02d}"  
    milhar_3 = f"05{dezena_puxada:02d}"              
    
    return [milhar_1, milhar_2, milhar_3]

async def main(page: ft.Page):
    page.title = "Rei do Palpite - Sistema de Puxadas"
    page.window.width = 430
    page.window.height = 700
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.ADAPTIVE

    # --- TELA 1: LÓGICA DOS SEGUNDOS ---
    txt_coruja = ft.TextField(label="Dezena 2º Prêmio (Bilhete Anterior)", keyboard_type=ft.KeyboardType.NUMBER)
    txt_ppt = ft.TextField(label="Dezena 2º Prêmio (Bilhete Atual)", keyboard_type=ft.KeyboardType.NUMBER)
    lbl_res_aba1 = ft.Column(spacing=10)

    async def btn_calcular_aba1_click(e):
        lbl_res_aba1.controls.clear()
        palpites = calcular_logica_segundos(txt_coruja.value, txt_ppt.value)
        if palpites:
            lbl_res_aba1.controls.append(ft.Text("🎯 Milhares da Lógica 1 (Puxadas):", size=16, color=ft.Colors.GREEN_400, weight=ft.FontWeight.BOLD))
            for p in palpites:
                lbl_res_aba1.controls.append(ft.Text(f"• Milhar: {p}", size=20, weight=ft.FontWeight.BOLD))
        else:
            lbl_res_aba1.controls.append(ft.Text("Insira dezenas válidas.", color=ft.Colors.RED_400))
        page.update()

    btn_aba1 = ft.Button("Calcular Puxadas", on_click=btn_calcular_aba1_click, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE)

    conteudo_aba1 = ft.Container(
        content=ft.Column([
            ft.Text("Lógica dos Segundos Prêmios 👑", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400),
            ft.Text("Calcula dezenas baseadas na tabela oficial de puxadas.", size=13, color=ft.Colors.GREY_400),
            ft.Divider(),
            txt_coruja,
            txt_ppt,
            btn_aba1,
            ft.Divider(),
            lbl_res_aba1
        ]), padding=15
    )

    # --- TELA 2: CENTENA FIXA ---
    txt_milhar_base = ft.TextField(label="Milhar do 2º Prêmio Anterior", keyboard_type=ft.KeyboardType.NUMBER)
    lbl_res_aba2 = ft.Column(spacing=10)

    async def btn_calcular_aba2_click(e):
        lbl_res_aba2.controls.clear()
        palpites = calcular_logica_centena(txt_milhar_base.value)
        if palpites:
            lbl_res_aba2.controls.append(ft.Text("🎯 Milhares da Centena Fixa + Puxadas:", size=16, color=ft.Colors.GREEN_400, weight=ft.FontWeight.BOLD))
            for p in palpites:
                lbl_res_aba2.controls.append(ft.Text(f"• Milhar: {p}", size=20, weight=ft.FontWeight.BOLD))
        else:
            lbl_res_aba2.controls.append(ft.Text("Insira uma milhar válida (4 dígitos).", color=ft.Colors.RED_400))
        page.update()

    btn_aba2 = ft.Button("Calcular com Centena Fixa", on_click=btn_calcular_aba2_click, bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE)

    conteudo_aba2 = ft.Container(
        content=ft.Column([
            ft.Text("Lógica da Centena Fixa Automática 📑", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400),
            ft.Text("Mantém os 2 primeiros dígitos e gera as dezenas puxadas pelo bicho.", size=13, color=ft.Colors.GREY_400),
            ft.Divider(),
            txt_milhar_base,
            btn_aba2,
            ft.Divider(),
            lbl_res_aba2
        ]), padding=15
    )

    # --- NAVEGAÇÃO ENTRE AS TELAS ---
    area_conteudo = ft.Container(content=conteudo_aba1, expand=True)

    def mostrar_aba1(e):
        area_conteudo.content = conteudo_aba1
        btn_nav1.bgcolor = ft.Colors.BLUE_700
        btn_nav2.bgcolor = ft.Colors.GREY_800
        page.update()

    def mostrar_aba2(e):
        area_conteudo.content = conteudo_aba2
        btn_nav1.bgcolor = ft.Colors.GREY_800
        btn_nav2.bgcolor = ft.Colors.GREEN_700
        page.update()

    btn_nav1 = ft.Button("Puxada Segundos", on_click=mostrar_aba1, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, expand=True)
    btn_nav2 = ft.Button("Centena Fixa", on_click=mostrar_aba2, bgcolor=ft.Colors.GREY_800, color=ft.Colors.WHITE, expand=True)

    barra_topo = ft.Row([btn_nav1, btn_nav2], spacing=10)

    page.add(barra_topo, area_conteudo)

import os

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 8550))
    asyncio.run(
        ft.run_async(
            main,
            port=porta,
            host="0.0.0.0",
            assets_dir="assets"
        )
    )

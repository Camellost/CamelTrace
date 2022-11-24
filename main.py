#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
	ISO-8859-1 - nao listado
	
	STATUS: 20

	CAMELTRACE CRIACAO E AUTOMATIZACAO DE DESENHOS COM O MOUSE! COMPATIVEL CAPAZ DE FUNCIONAR CONJUTAMENTE COM VARIOS PROGRAMAS DE DESENHOS
	CAMELTRACE FOI CRIADO PARA FINS EDUCATIVOS NAO LUCRATIVOS!

	AUTOR: EMERSON MACIEL - MAGIOZ
	CONTATO: CAMELLOST.RF.GD@GMAIL.COM 

	STATUS: 12
	
	Altenativas: para controle do mouse com pyautogui (https://github.com/asweigart/pyautogui)
	
	Os elementos do caminho são derivados de outros projetos de svgelements (https://github.com/meerk40t/svgelements/tree/master/svgelements)

	Filtros adicionados PIL/Pillow para bitmaps (https://python-pillow.org/) fornecido (https://github.com/python-pillow/Pillow)

	
	2022 Camellost (c) - Emerson Maciel

"""

import os
import sys
import locale
import time
import re
import io
import json
import tempfile
import shutil

import threading
import keyboard
import subprocess
import pyautogui

from svgelements import *
from pickle import dump, load
from math import sqrt
from random import randint
from PIL import Image, ImageFilter

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtSvgWidgets import *
from PySide6.QtSvg import *

import recursos

try:
	locale.setlocale(locale.LC_ALL, QLocale.system().name())
except:
	locale.setlocale(locale.LC_ALL, 'pt_BR')

__appname__ = "CamelTrace"
__version__ = "2.12"
__author__ = "Emerson Maciel"
__email__ = "camellost.rf.gd@gmail.com"
__language__ = "pt_BR"
__license__ = "MIT"
__status__ = "Release"

"""
	GLOBAL GLOBAL

"""

LOCAL_CONFIG_JSON = os.path.join('data', 'config', 'config.json')
LOCAL_TEMP_SVG = os.path.join('data', 'temp', 'svg_temp.svg')
LOCAL_TEMP_SVG_P = os.path.join('data', 'temp', 'svg_pre_temp.svg')
LOCAL_IDIOMAS = os.path.join('data', 'idiomas', '')

C_LOCAL_TEMP_SVG = LOCAL_TEMP_SVG.replace('\\', '/')
C_LOCAL_TEMP_SVG_P = LOCAL_TEMP_SVG_P.replace('\\', '/')

LOCAL_DESENHOS = os.path.join('data', 'desenhos')
LOCAL_SVG = os.path.join(LOCAL_DESENHOS, 'svgs')
LOCAL_LINHAS = os.path.join(LOCAL_DESENHOS, 'linhas')
LOCAL_JSON = os.path.join(LOCAL_DESENHOS, 'json')
LOCAL_TEMA = os.path.join('data', 'tema')

LOCAL_TEMA_ESCURO_CAMELTRACE = os.path.join(LOCAL_TEMA, 'escuro.cestilo')
LOCAL_TEMA_CLARO_CAMELTRACE = os.path.join(LOCAL_TEMA, 'claro.cestilo')

"""
	GLOBAL GLOBAL

"""

pyautogui.PAUSE = 0.003
pyautogui.FAILSAFE = False

DATA_TELA_VISUALIZAR = None

GLOBAL_BITMAP = None
GLOBAL_ALTURA = None
GLOBAL_LARGURA = None
GLOBAL_SVG = None


PROPORCAO_ESTADO = None

TOTAL_DESENHO = None
ARGUMENTOS = None


CONFIG_TEMA = None
CONFIG_AVISO = None
CONFIG_TEMPO_ATUALIZAR = None
CONFIG_TEMPO_PAUSA = None
CONFIG_COR_BORDA = None
CONFIG_ATALHO_INICIAR = None
CONFIG_ATALHO_PARAR = None
CONFIG_ATALHO_PAUSAR = None
CONFIG_OTIMIZAR = None
CONFIG_TEMPO_ESPERA = None

GET_LINHAS = None
GET_SVG = None
GET_NOME = None
GET_PONTOS = None
XPOS = 300
YPOS = 0

ULTIMO_DESENHO_NOME = None
ULTIMO_XPOS = None
ULTIMO_YPOS = None

def reiniciar_cameltrace():

	# REINICIA O CAMELTRACE E LIBERA OS WIDGETS EM QCoreApplication.quit

	QCoreApplication.quit()
	executar = QProcess.startDetached(sys.executable, sys.argv)

def liberar_memoria():

	# OPICIONAL: ReduceMemory LIBERA A MEMORIA DO CAMELTRACE EM ALGUMAS SESSOES DE PAGINACAO, O CAMELTRACE INICIA ENTRE 90/50mb MEMORIA RAM, COM ReduceMemory 27mb
	# ADICIONE OS EXECUTAVEL NA PASTA CAMELTRACE ONDE ESTÁ O PROGRAMA... PARA ATIVAR A OTIMIZAÇÃO
	
	try:
		sistema_ph = sys.maxsize > 2**32
		if sistema_ph == True:
			arg_reduce = 'ReduceMemory_x64.exe /O cameltrace.exe'
		else:
			arg_reduce = 'ReduceMemory.exe /O cameltrace.exe'
		processo_otimizar = subprocess.Popen(arg_reduce, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
		processo_otimizar.communicate()
		return True
	except:
		return False

class Mensagem(QMessageBox):
	def __init__(self, parent, tipo = QMessageBox.Warning, msg = "Camellost - CamelTrace", titulo = "CamelTrace", btn = QMessageBox.Ok | QMessageBox.Cancel):
		super().__init__(parent)
		self.setParent(parent)
		QApplication.beep()
		self.setIcon(tipo)
		self.setText(str(msg))
		self.setWindowTitle(str(titulo))
		self.setStandardButtons(btn)
		self.buttonClicked.connect(self.reject)

class EditarJson:
	def __init__(self, path_json=None, valor="", sjt="", tipo="Salvar"):
		super().__init__()
		with open(path_json, 'r') as arquivo, tempfile.NamedTemporaryFile('w', delete=False) as outemp:
			dados = json.load(arquivo)
			if tipo == "Salvar":
				dados[f"{valor}"] = sjt
			elif tipo == "Adicionar":
				dados[f"{valor}"].insert(0, sjt)
			elif tipo == "Remover":
				if sjt in dados:
					del dados[sjt]
			json.dump(dados, outemp, ensure_ascii=False, indent=4, separators=(',',':'))
		shutil.move(outemp.name, path_json)

class Criador_Config_Pasta:
	def __init__(self):
		super().__init__()
		"""
		COMPARTIBILIDADE VERIFICA E CRIA PASTA QUE ESTEJAM FALTANDO NO CAMELTRACE

		USANDO OS.PATH.JOIN CRIA UM CAMINHO DE DIRETORIOS EM (string)

		VERIFICA OS.PATH.EXISTS VERIFICA SE O CAMINHO EXISTE RETORNA Verdadeiro ou Falso

		"""

		self.LOCAL_PST_DESENHO = os.path.join('data', 'desenhos')
		self.LOCAL_PST_TEMA = os.path.join('data', 'tema')
		self.LOCAL_PST_JSON = os.path.join(self.LOCAL_PST_DESENHO, 'json')
		self.LOCAL_PST_SVG = os.path.join(self.LOCAL_PST_DESENHO, 'svgs') 
		self.LOCAL_PST_LINHAS = os.path.join(self.LOCAL_PST_DESENHO, 'linhas') 
		self.LOCAL_PST_CONFIG = os.path.join('data', 'config') 
		self.LOCAL_PST_TEMP = os.path.join('data', 'temp')
		self.LOCAL_CONFIG_JSON = os.path.join('data', 'config', 'config.json')

		self.LOCAL_PST_TEMA_EXIST = os.path.exists(self.LOCAL_PST_TEMA) 
		self.LOCAL_PST_DESENHO_EXIST = os.path.exists(self.LOCAL_PST_DESENHO) 
		self.LOCAL_PST_JSON_EXIST = os.path.exists(self.LOCAL_PST_JSON)
		self.LOCAL_PST_SVG_EXIST = os.path.exists(self.LOCAL_PST_SVG)
		self.LOCAL_PST_LINHAS_EXIST = os.path.exists(self.LOCAL_PST_LINHAS)
		self.LOCAL_PST_CONFIG_EXIST = os.path.exists(self.LOCAL_PST_CONFIG)
		self.LOCAL_PST_TEMP_EXIST = os.path.exists(self.LOCAL_PST_TEMP)
		self.LOCAL_CONFIG_JSON_EXISTE = os.path.exists(self.LOCAL_CONFIG_JSON)

	def ac_verificar_pasta(self):
		if self.LOCAL_PST_TEMA_EXIST == False:
			os.mkdir(self.LOCAL_PST_TEMA)
		if self.LOCAL_PST_DESENHO_EXIST == False:
			os.mkdir(self.LOCAL_PST_DESENHO)
		if self.LOCAL_PST_JSON_EXIST == False:
			os.mkdir(self.LOCAL_PST_JSON)
		if self.LOCAL_PST_SVG_EXIST == False:
			os.mkdir(self.LOCAL_PST_SVG)
		if self.LOCAL_PST_LINHAS_EXIST == False:
			os.mkdir(self.LOCAL_PST_LINHAS)
		if self.LOCAL_PST_CONFIG_EXIST == False:
			os.mkdir(self.LOCAL_PST_CONFIG)
		if self.LOCAL_PST_TEMP_EXIST == False:
			os.mkdir(self.LOCAL_PST_TEMP)

		try:
			self.ac_criar_config(self.LOCAL_CONFIG_JSON_EXISTE)
		except Exception as e:
			msg = Mensagem(self, QMessageBox.Critical, f"Erro ao criar configurações: {e}", u"Erro ao criar configurações", QMessageBox.Ok)
			msg.exec()

	def ac_criar_config(self, entrada = None):
		"""
		CRIA CONFIGURAÇÃO GLOBAL DO CAMELTRACE PODENDO SER EDITAR NO ARQUIVO JSON DE CONFIGURAÇÃO
		
		"""
		if entrada == True:
			pass
		else:
			config_data = {'Tema': ['Light', 0], 'Aviso': False,'Tempo_Atualizar': 250, 'Tempo_Pausa': 0.003, 'Cor_Borda': '#ff0000', 'Atalho_Iniciar': 'CTRL+B', 'Atalho_Parar': 'CTRL+L', 'Atalho_Pausar': 'CTRL+SHIFT+J', 'Tempo_Espera': [False, 0], 'Auto_Otimizar': False}
			with open(self.LOCAL_CONFIG_JSON, 'w', encoding='utf-8') as salvar_config:
				json.dump(config_data, salvar_config, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))
		
		self.initConfig()

	def initConfig(self):

		"""
		DEFINE TODAS A CONFIGURAÇÕES GLOBAL PARA SER ACESSADO
		
		"""
		global CONFIG_TEMA
		global CONFIG_AVISO
		global CONFIG_TEMPO_ATUALIZAR
		global CONFIG_TEMPO_PAUSA
		global CONFIG_COR_BORDA
		global CONFIG_ATALHO_INICIAR
		global CONFIG_ATALHO_PARAR
		global CONFIG_ATALHO_PAUSAR
		global CONFIG_TEMPO_ESPERA
		global CONFIG_OTIMIZAR

		with open(self.LOCAL_CONFIG_JSON) as abrir_config:
			ler_config = json.load(abrir_config)
			CONFIG_TEMA = ler_config['Tema']
			CONFIG_AVISO = ler_config['Aviso']
			CONFIG_TEMPO_ATUALIZAR = ler_config['Tempo_Atualizar']
			CONFIG_TEMPO_PAUSA = ler_config['Tempo_Pausa']
			CONFIG_COR_BORDA = ler_config['Cor_Borda']
			CONFIG_ATALHO_INICIAR = ler_config['Atalho_Iniciar']
			CONFIG_ATALHO_PARAR = ler_config['Atalho_Parar']
			CONFIG_ATALHO_PAUSAR = ler_config['Atalho_Pausar']
			CONFIG_TEMPO_ESPERA = ler_config['Tempo_Espera']
			CONFIG_OTIMIZAR = ler_config['Auto_Otimizar']
			pyautogui.PAUSE = CONFIG_TEMPO_PAUSA

class Combo_Personalizado(QComboBox):
	fade = Signal()
	def __init__(self, parent):
		super().__init__(parent)

		self.setParent(parent)

		self.style = QStyledItemDelegate()
		self.setItemDelegate(self.style)
		self.view().window().setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
		self.view().window().setAttribute(Qt.WA_TranslucentBackground)

		self.showPopup()

	@Slot(bool)
	def showPopup(self, emit=True):
		if emit:
			self.fade.emit()
		super().showPopup()
		popup = self.findChild(QFrame)

		#efeito = QGraphicsOpacityEffect(popup, opacity=1.0)
		#popup.setGraphicsEffect(efeito)
		#popup.efeito_fade = QPropertyAnimation(popup, propertyName=b"opacity", targetObject=efeito, duration=400, startValue=0.0, endValue=1.0)
		#popup.efeito_fade.setDirection(QPropertyAnimation.Forward)

		self.largura  = popup.width()
		self.altura  = popup.height()
		self.porcentagem =  int(self.altura - int(self.altura * 0.40))
		self.efeito_arrasta = QPropertyAnimation(popup, b"size")
		self.efeito_arrasta.setStartValue(QSize(self.largura , self.porcentagem))
		self.efeito_arrasta.setEndValue(QSize(self.largura, self.altura))
		self.efeito_arrasta.setEasingCurve(QEasingCurve.Linear)
		self.efeito_arrasta.setDuration(150)

		self.grupo_efeitos = QParallelAnimationGroup()
		#self.grupo_efeitos.addAnimation(popup.efeito_fade)
		self.grupo_efeitos.addAnimation(self.efeito_arrasta)
		self.grupo_efeitos.start()

class Menu_Personalizado(QMenu):
	def __init__(self, parent):
		super(Menu_Personalizado, self).__init__(parent)
		self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
		self.setAttribute(Qt.WA_TranslucentBackground)
		self.setParent(parent)
		#self.installEventFilter(self)
	def showEvent(self, event):
		# do stuff here 
		#self.append('This random text string ')
		self.showEfeito()
		event.accept()
	@Slot()	
	def showEfeito(self):

		#efeito = QGraphicsOpacityEffect(self, opacity=1.0)
		#self.setGraphicsEffect(efeito)

		#self.efeito_fade = QPropertyAnimation(self, propertyName=b"opacity", targetObject=efeito, duration=400, startValue=0.0, endValue=1.0)
		#self.efeito_fade.setEasingCurve(QEasingCurve.InOutCubic)
		#self.efeito_fade.setDirection(QPropertyAnimation.Forward)
		self.porcentagem =  int(self.height() - int(self.height() * 0.40))

		self.efeito_arrasta = QPropertyAnimation(self, b"size")
		self.efeito_arrasta.setStartValue(QSize(self.width() , self.porcentagem))
		self.efeito_arrasta.setEndValue(QSize(self.width(), self.height()))
		self.efeito_arrasta.setEasingCurve(QEasingCurve.Linear)
		self.efeito_arrasta.setDuration(150)

		self.grupo_efeitos = QParallelAnimationGroup()
		#self.grupo_efeitos.addAnimation(self.efeito_fade)
		self.grupo_efeitos.addAnimation(self.efeito_arrasta)
		self.grupo_efeitos.start()

class Botao_Personalizado(QToolButton):
	def __init__(self, parent, pagina):
		super(Botao_Personalizado, self).__init__(parent)

		self.setParent(parent)
		self.pagina = pagina

	@Slot(bool)
	def setAtivo(self, ativo):
		self.ativo = ativo
		if CONFIG_TEMA[0] == "Light":
			ccor = u"0, 0, 0"
		else:
			ccor = u"255, 255, 255"


		if self.ativo == True:
			self.setStyleSheet(f"""
QToolButton{{
	background-color: rgba({ccor}, 10);
}}
QToolButton:hover{{
	background-color: rgba({ccor}, 8);
}}
				""")
		else:
			self.setStyleSheet(f"""

QToolButton{{
	background-color: none;
}}
QToolButton:hover{{
	background-color: rgba({ccor}, 15);
}}
				""")

class Botao_Drop_Personalizado(QToolButton):
	def __init__(self, parent = None, tamanho = 100):
		super().__init__(parent)
		self.parent = parent
		self.setAcceptDrops(True)
		self.setMinimumSize(QSize(tamanho, tamanho))
		self.setMaximumSize(QSize(tamanho, tamanho))
		self.setCursor(QCursor(Qt.PointingHandCursor))
		self.setIconSize(QSize(tamanho, tamanho))
		self.clicked.connect(self.ac_img)

	@Slot()
	def ac_img(self):
		try:
			caminho, _ = QFileDialog.getOpenFileName(self, 'Abrir Arquivo de Imagem', 'c:\\',"Arquivo de Imagem (*.jpg *.jfif *.gif *.png *.jpge *.bmp *.ico *.webp *.mpeg *.tiff *.jpeg)")
			self.parent.ac_abrir_imagem(caminho)
		except Exception as e:
			msg = Mensagem(self, QMessageBox.Critical, self.tr("Erro Inesperado: ") + str(e) , self.tr(u"Erro Inesperado"), QMessageBox.Ok)
			msg.exec()  

	@Slot(str)
	def ac_adicionar_img(self, caminho = None):
		self.caminho = caminho
		try:
			self.parent.ac_abrir_imagem(self.caminho)
		except Exception as e:
			msg = Mensagem(self, QMessageBox.Critical, self.tr(u"Erro ao arrastar a imagem: ") + str(e), self.tr(u"Erro ao arrastar a imagem"), QMessageBox.Ok)
			msg.exec()

	def dragEnterEvent(self, event):
		if event.mimeData().hasImage:
			event.accept()
		else:
			event.ignore()
	def dragMoveEvent(self, event):
		if event.mimeData().hasImage:
			event.accept()
		else:
			event.ignore()
	def dropEvent(self, event):
		if event.mimeData().hasImage:
			event.setDropAction(Qt.CopyAction)
			local_img = event.mimeData().urls()[0].toLocalFile()
			self.ac_adicionar_img(local_img)
			event.accept()
		else:
			event.ignore()

class CamelPreSvg(QSvgWidget):
	fechar = Signal()

	def __init__(self, *args, **kwargs):
		super(CamelPreSvg, self).__init__(*args, **kwargs)
		self.setObjectName(u"CamelPreSvg")
		self.setWindowIcon(QIcon(u":/icones/Logo-CamelTrace-Preenchido.svg"))
		self.setWindowTitle("Pré-visualizar desenho")
		self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
		self.setAttribute(Qt.WA_TranslucentBackground)
		self.move(XPOS, YPOS)
		self.setStyleSheet(f"""
#CamelPreSvg{{
	background-color: rgba(255, 255, 255, 50);
	border: 1px solid {CONFIG_COR_BORDA};
}}
#tela_cima{{
	background-color: rgba(255, 255, 255, 200);

}}
#rotulo_info{{
	color: rgb(48, 121, 214);
	font: 700 10pt "Arial";
}}
			""")
		self.load(GET_SVG)
		self.vertical = QVBoxLayout(self)
		self.tela_cima = QFrame(self)
		self.tela_cima.setObjectName(u"tela_cima")
		self.tela_cima.setFrameShape(QFrame.StyledPanel)
		self.tela_cima.setFrameShadow(QFrame.Raised)
		self.horizontal = QHBoxLayout(self.tela_cima)
		self.horizontal.setContentsMargins(5, 5, 5, 5)
		self.rotulo_info = QLabel(self.tela_cima)
		self.rotulo_info.setObjectName(u"rotulo_info")
		self.rotulo_info.setAlignment(Qt.AlignCenter)
		self.rotulo_info.setText(f"X: {XPOS}\nY: {YPOS}")
		self.horizontal.addWidget(self.rotulo_info)
		self.vertical.addWidget(self.tela_cima, 0, Qt.AlignTop)
		try:
			self.leaveEvent = lambda e: self.tela_cima.hide()
			self.enterEvent = lambda e: self.tela_cima.show()
		except:
			...
			
		self.setLayout(self.vertical)

		self.show()

	def mousePressEvent(self, event):
		if event.button() == Qt.LeftButton:
			self.offset = QPoint(event.position().x(),event.position().y())
		else:
			super().mousePressEvent(event)

	def mouseMoveEvent(self, event):
		global XPOS
		global YPOS
		if self.offset is not None and event.buttons() == Qt.LeftButton:
			posicao = self.pos() + QPoint(event.scenePosition().x(),event.scenePosition().y()) - self.offset
			self.move(posicao)
			XPOS = posicao.x()
			YPOS = posicao.y()
			self.rotulo_info.setText(f"X: {XPOS}\nY: {YPOS}")
		else:
			super().mouseMoveEvent(event)

	def mouseReleaseEvent(self, event):
		self.offset = None
		super().mouseReleaseEvent(event)

class CamelDesenho(QWidget):
	def __init__(self, parent, nome, altura, largura, pontos, local_svg, local_lines, local_json, data, horas, tempo_desenho, categoria, tracar, tracar_senha, velocidade, local_svg_b):
		super(CamelDesenho, self).__init__(parent)
		self.parent = parent
		self.nome = nome
		self.altura = altura
		self.largura = largura
		self.pontos = pontos
		self.local_svg = local_svg
		self.local_lines = local_lines
		self.local_json = local_json
		self.data = data
		self.horas = horas
		self.tempo_desenho = tempo_desenho
		self.categoria = categoria
		self.tracar = tracar
		self.tracar_senha = tracar_senha
		self.velocidade = velocidade
		self.local_svg_b = local_svg_b

		self.pix_trancado = QPixmap(u":/icones/Trancado.svg")
		self.pix_trancado = self.pix_trancado.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
		if CONFIG_TEMA[0] == "Light":
			self.pix = QPixmap(self.local_svg)
			self.pix = self.pix.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
		else:
			self.pix = QPixmap(self.local_svg_b)
			self.pix = self.pix.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
		self.setObjectName(u"CamelDesenho")
		self.m_layout = QVBoxLayout()
		self.m_layout.setContentsMargins(0,0,0,0)
		self.m_layout.setSpacing(0)
		self.conteudo_desenho = QWidget(self)
		self.conteudo_desenho.setObjectName(u"conteudo_desenho")
		self.conteudo_desenho.setMinimumSize(QSize(250, 380))
		self.conteudo_desenho.setMaximumSize(QSize(250, 380))
		self.verticalLayout = QVBoxLayout(self.conteudo_desenho)
		self.verticalLayout.setObjectName(u"verticalLayout")
		self.rotulo_nome_desenho = QLabel(self.conteudo_desenho)
		self.rotulo_nome_desenho.setObjectName(u"rotulo_nome_desenho")
		self.rotulo_nome_desenho.setMinimumSize(QSize(0, 35))
		self.rotulo_nome_desenho.setMaximumSize(QSize(16777215, 35))
		self.rotulo_nome_desenho.setAlignment(Qt.AlignCenter)
		self.rotulo_nome_desenho.setWordWrap(True)
		self.rotulo_nome_desenho.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)
		self.rotulo_nome_desenho.setText(u"{un}".format(un = self.nome))
		self.verticalLayout.addWidget(self.rotulo_nome_desenho)
		self.line = QFrame(self.conteudo_desenho)
		self.line.setObjectName(u"line")
		self.line.setFrameShadow(QFrame.Plain)
		self.line.setFrameShape(QFrame.HLine)
		self.verticalLayout.addWidget(self.line)
		self.rotulo_estimado = QLabel()
		self.rotulo_estimado.setObjectName(u"rotulo_estimado")
		self.rotulo_estimado.setMinimumSize(QSize(0, 20))
		self.rotulo_estimado.setMaximumSize(QSize(16777215, 20))
		self.rotulo_estimado.setAlignment(Qt.AlignCenter)
		self.rotulo_estimado.setWordWrap(True)

		if self.tempo_desenho != "":
			self.rotulo_estimado.setText(self.tr(u"Tempo estimado: ") + str(self.tempo_desenho))
		
		self.verticalLayout.addWidget(self.rotulo_estimado, 0, Qt.AlignTop)
		self.input_preview = QLabel(self.conteudo_desenho)
		self.input_preview.setObjectName(u"input_preview")
		self.input_preview.setAlignment(Qt.AlignCenter)
		self.verticalLayout.addWidget(self.input_preview)
		self.btn_desenhar = QPushButton(self.conteudo_desenho)
		self.btn_desenhar.setObjectName(u"btn_desenhar")
		self.btn_desenhar.setMinimumSize(QSize(0, 30))
		self.btn_desenhar.setMaximumSize(QSize(16777215, 30))
		self.btn_desenhar.setText(self.tr(u"Desenhar"))
		self.verticalLayout.addWidget(self.btn_desenhar, 0, Qt.AlignBottom)
		self.m_layout.addWidget(self.conteudo_desenho)

		if self.tracar == True or self.tracar == "Senha":
			self.btn_desenhar.setEnabled(False)
			self.input_preview.setPixmap(self.pix_trancado)
		else:
			self.btn_desenhar.setEnabled(True)
			self.input_preview.setPixmap(self.pix)

		self.setLayout(self.m_layout)

		self.btn_desenhar.clicked.connect(self.ac_iniciar_desenho)

	def contextMenuEvent(self, event):
		self.action_trancar = QAction(self.tr(u"Trancar Desenho"), self)
		self.action_trancar.setIcon(QIcon(u":/icones/Trancar.png"))
		self.action_trancar.triggered.connect(self.ac_tracar)
		self.action_destrancar = QAction(self.tr(u"Destrancar"), self)
		self.action_destrancar.setIcon(QIcon(u":/icones/Destrancar.png"))
		self.action_destrancar.triggered.connect(self.ac_destrancar)
		self.action_editar_nome = QAction(self.tr(u"Editar Nome"), self)
		self.action_editar_nome.setIcon(QIcon(u":/icones/Renomear.png"))
		self.action_editar_nome.triggered.connect(self.ac_editar_nome)
		self.action_visualizar = QAction(self.tr(u"Visualizar"), self)
		self.action_visualizar.setIcon(QIcon(u":/icones/Visivel.png"))
		self.action_visualizar.triggered.connect(self.ac_visualizar)
		self.action_info = QAction(self.tr(u"Informações"), self)
		self.action_info.setIcon(QIcon(u":/icones/Sobre.png"))
		self.action_info.triggered.connect(self.ac_info)
		self.action_excluir = QAction(self.tr(u"Excluir Desenho"), self)
		self.action_excluir.setIcon(QIcon(u":/icones/Cancelar.png"))
		self.action_excluir.triggered.connect(self.ac_excluir)
		self.action_exportar = QAction(self.tr(u"Exportar Coordenadas"), self)
		self.action_exportar.setIcon(QIcon(u":/icones/Exportar.png"))
		self.action_exportar.triggered.connect(self.ac_exportar)

		self.menu = Menu_Personalizado(self)

		if self.tracar == True or self.tracar == "Senha":
			self.menu.addAction(self.action_destrancar)
		else:
			self.menu.addAction(self.action_trancar)
			self.menu.addAction(self.action_editar_nome)
			self.menu.addAction(self.action_visualizar)
			self.menu.addAction(self.action_info)
			self.menu.addAction(self.action_exportar)
			self.menu.addSeparator()
			self.menu.addAction(self.action_excluir)

		self.menu.exec(self.mapToGlobal(event.pos()))

	def ac_ocultar(self):
		self.input_preview.hide()

	def ac_exibir(self):
		self.input_preview.show()

	def ac_info(self):
		try:
			l1 = self.tr(u"Nome do Desenho: ") + self.nome
			l2 = self.tr(u"Altura: ") + str(self.altura)
			l3 = self.tr(u"Largura: ") + str(self.largura)
			l4 = self.tr(u"N° Densidade: ") + str(self.pontos) + f" - ({self.velocidade})"
			l5 = self.tr(u"Tempo Estimado: ") + self.tempo_desenho
			l6 = self.tr(u"Caminho data: ") + self.local_json
			l7 = self.tr(u"Criado em ") + self.data + self.tr(u" as ") + self.horas

			msg = Mensagem(self, QMessageBox.Information, f"{l1}\n{l2}\n{l3}\n{l4}\n{l5}\n{l6}\n{l7}", f"Informações | {self.nome}", QMessageBox.Ok)
			msg.exec()
		except Exception as e:
			msg = Mensagem(self, QMessageBox.Critical, self.tr(u"Erro ao exibir as informações: ") + str(e), self.tr(u"Erro ao exibir as informações"), QMessageBox.Ok)
			msg.exec()

	@Slot() 
	def ac_tracar(self):
		try:
			self.caixa_trancar = QDialog(self)
			self.caixa_trancar.setWindowIcon(QIcon(u":/icones/Trancar.png"))
			self.caixa_trancar.setObjectName(u"caixa_trancar")
			self.caixa_trancar.setWindowTitle(self.tr(u"Trancar desenho"))

			verticalLayout = QVBoxLayout(self.caixa_trancar)
			verticalLayout.setObjectName(u"verticalLayout")
			self.grupo_senha = QGroupBox(self.caixa_trancar)
			self.grupo_senha.setObjectName(u"grupo_senha")
			self.grupo_senha.setCheckable(True)
			self.grupo_senha.setChecked(True)
			self.grupo_senha.setTitle(self.tr(u"Trancar desenho com senha"))
			verticalLayout_2 = QVBoxLayout(self.grupo_senha)
			verticalLayout_2.setObjectName(u"verticalLayout_2")
			self.input_senha = QLineEdit(self.grupo_senha)
			self.input_senha.setObjectName(u"input_senha")
			self.input_senha.setMinimumSize(QSize(0, 30))
			self.input_senha.setMaximumSize(QSize(16777215, 30))
			self.input_senha.setMaxLength(50)
			self.input_senha.setEchoMode(QLineEdit.PasswordEchoOnEdit)
			self.input_senha.setClearButtonEnabled(True)
			self.input_senha.setPlaceholderText(self.tr(u"Senha"))
			verticalLayout_2.addWidget(self.input_senha)
			self.input_confimar_senha = QLineEdit(self.grupo_senha)
			self.input_confimar_senha.setObjectName(u"input_confimar_senha")
			self.input_confimar_senha.setMinimumSize(QSize(0, 30))
			self.input_confimar_senha.setMaximumSize(QSize(16777215, 30))
			self.input_confimar_senha.setMaxLength(50)
			self.input_confimar_senha.setEchoMode(QLineEdit.Password)
			self.input_confimar_senha.setClearButtonEnabled(True)
			self.input_confimar_senha.setPlaceholderText(self.tr(u"Confimar Senha"))
			verticalLayout_2.addWidget(self.input_confimar_senha)
			verticalLayout.addWidget(self.grupo_senha, 0, Qt.AlignTop)
			self.buttonBox = QDialogButtonBox(self.caixa_trancar)
			self.buttonBox.setObjectName(u"buttonBox")
			self.buttonBox.setOrientation(Qt.Horizontal)
			self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
			self.buttonBox.setCenterButtons(False)
			verticalLayout.addWidget(self.buttonBox)
			self.buttonBox.accepted.connect(self.ac_trancar_desenho)
			self.buttonBox.rejected.connect(self.caixa_trancar.reject)

			self.caixa_trancar.exec()
		except Exception as e:
			msg = Mensagem(self, QMessageBox.Critical, self.tr(u"Erro ao abrir QDialog: ") + str(e), u"Erro", QMessageBox.Ok)
			msg.exec()

	def ac_trancar_desenho(self):
		if self.grupo_senha.isChecked() == True:
			if self.input_senha.text() != self.input_confimar_senha.text():
				msg = Mensagem(self, QMessageBox.Critical, self.tr(u"Senhas não são iguais"), "Erro", QMessageBox.Ok)
				msg.exec()
			elif self.input_senha.text() == "" or self.input_confimar_senha.text() == "":
				msg = Mensagem(self, QMessageBox.Critical, self.tr(u"Campo vazio"), "Erro", QMessageBox.Ok)
				msg.exec()
			else:
				EditarJson(self.local_json, "Trancado", "Senha")
				EditarJson(self.local_json, "Trancado_Senha", self.input_senha.text())
				self.tracar_senha = self.input_senha.text()
				self.input_preview.setPixmap(self.pix_trancado)
				self.tracar = "Senha"
				self.btn_desenhar.setEnabled(False)
				self.caixa_trancar.accept()
		else:
			EditarJson(self.local_json, "Trancado", True)
			self.input_preview.setPixmap(self.pix_trancado)
			self.tracar = True
			self.btn_desenhar.setEnabled(False)
			self.caixa_trancar.accept()

	def ac_destrancar(self):
		if self.tracar == "Senha":
			self.caixa_destrancar = QDialog(self)
			self.caixa_destrancar.setWindowIcon(QIcon(u":/icones/Destrancar.png"))
			self.caixa_destrancar.setObjectName(u"caixa_destrancar")
			self.caixa_destrancar.setWindowTitle(self.tr(u"Destrancar desenho"))
			verticalLayout = QVBoxLayout(self.caixa_destrancar)
			verticalLayout.setObjectName(u"verticalLayout")
			self.label = QLabel(self.caixa_destrancar)
			self.label.setObjectName(u"label")
			self.label.setText(self.tr(u"Digite a senha para destrancar o desenho"))

			verticalLayout.addWidget(self.label)

			self.input_senha_destrancar = QLineEdit(self.caixa_destrancar)
			self.input_senha_destrancar.setObjectName(u"input_senha_destrancar")
			self.input_senha_destrancar.setMinimumSize(QSize(0, 30))
			self.input_senha_destrancar.setMaximumSize(QSize(16777215, 30))
			self.input_senha_destrancar.setMaxLength(50)
			self.input_senha_destrancar.setEchoMode(QLineEdit.PasswordEchoOnEdit)
			self.input_senha_destrancar.setClearButtonEnabled(True)
			self.input_senha_destrancar.setPlaceholderText(self.tr(u"Senha"))

			verticalLayout.addWidget(self.input_senha_destrancar)

			self.buttonBox = QDialogButtonBox(self.caixa_destrancar)
			self.buttonBox.setObjectName(u"buttonBox")
			self.buttonBox.setOrientation(Qt.Horizontal)
			self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
			self.buttonBox.setCenterButtons(False)

			verticalLayout.addWidget(self.buttonBox)

			self.buttonBox.accepted.connect(self.ac_destrancar_desenho)
			self.buttonBox.rejected.connect(self.caixa_destrancar.reject)

			self.caixa_destrancar.exec()
		else:
			EditarJson(self.local_json, "Trancado", False)
			self.tracar = False
			self.input_preview.setPixmap(self.pix)
			self.btn_desenhar.setEnabled(True)

	def ac_destrancar_desenho(self):
		if self.input_senha_destrancar.text() == self.tracar_senha:
			EditarJson(self.local_json, "Trancado", False)
			EditarJson(self.local_json, "Trancado_Senha", "")
			self.tracar = False
			self.btn_desenhar.setEnabled(True)
			self.input_preview.setPixmap(self.pix)
			self.caixa_destrancar.accept()
		else:
			msg = Mensagem(self, QMessageBox.Critical, self.tr(u"Senha incorreta"), u"Erro", QMessageBox.Ok)
			msg.exec()

	@Slot()		
	def ac_editar_nome(self):
		try:
			self.caixa = QDialog(self)
			self.caixa.setWindowIcon(QIcon(u":/icones/Renomear.png"))
			self.caixa.setWindowTitle(self.tr(u"Editar nome do desenho"))
			vertical = QVBoxLayout(self.caixa)
			rotulo = QLabel(self.caixa)
			rotulo.setText(self.tr(u"Novo nome para o desenho:"))
			rotulo.setMaximumSize(QSize(16777215, 30))
			vertical.addWidget(rotulo)
			self.input_new = QLineEdit(self.caixa)
			self.input_new.setObjectName(u"input_new")
			self.input_new.setMinimumSize(QSize(0, 25))
			self.input_new.setMaximumSize(QSize(16777215, 25))
			self.input_new.setPlaceholderText(self.tr(u"Nome do desenho"))
			self.input_new.setMaxLength(27)
			self.input_new.setClearButtonEnabled(True)
			vertical.addWidget(self.input_new)
			self.buttonBox = QDialogButtonBox(self.caixa)
			self.buttonBox.setObjectName(u"buttonBox")
			self.buttonBox.setOrientation(Qt.Horizontal)
			self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
			self.buttonBox.setCenterButtons(False)
			vertical.addWidget(self.buttonBox)
			self.buttonBox.rejected.connect(self.caixa.reject)
			self.buttonBox.accepted.connect(self.ac_alterar_nome)

			self.caixa.exec()
		except Exception as e:
			msg = Mensagem(self, QMessageBox.Critical, self.tr("Erro ao abrir QDialog: ") + str(e), u"Erro", QMessageBox.Ok)
			msg.exec()

	def ac_alterar_nome(self):
		self.nome = self.input_new.text()
		if self.nome == "":
			msg = Mensagem(self, QMessageBox.Critical, self.tr(u"Erro: Campo nome vazio, por favor adicione um novo nome"), self.tr(u"Erro campo vazio"), QMessageBox.Ok)
			msg.exec()
		else:
			try:
				EditarJson(self.local_json, "Nome_Desenho", self.nome)
				self.rotulo_nome_desenho.setText(u"{tt}".format(tt = self.nome))
				self.caixa.accept()
			except:
				msg = Mensagem(self, QMessageBox.Critical, self.tr(u"Erro ao salvar o novo nome para o desenho"), self.tr(u"Erro ao salvar"), QMessageBox.Ok)
				msg.exec()

	@Slot()
	def ac_visualizar(self):
		self.view_svg = QSvgWidget()
		self.view_svg.setWindowTitle(self.tr(u"Visualizar " + self.nome))
		self.view_svg.setWindowIcon(self.parent.icone_cameltrace_window)
		self.view_svg.load(self.local_svg)
		self.view_svg.show()

	@Slot()
	def ac_excluir(self):
		global TOTAL_DESENHO

		try:
			msg = Mensagem(self, QMessageBox.Warning, self.tr(u"Deseja realmente excluir o desenho ") + self.nome + " ?", self.tr(u"Excluir ") + self.nome, QMessageBox.Ok | QMessageBox.Cancel)
			resultado = msg.exec()
			if resultado == QMessageBox.Ok:
				os.remove(self.local_json)
				os.remove(self.local_lines)
				os.remove(self.local_svg)
				os.remove(self.local_svg_b)
				self.parent.barra_estado.showMessage(self.tr(u"Desenho excluido com sucesso: ") + self.nome, 2000)
				for row in range(self.parent.lista_conteudo.count()):
					itens = self.parent.lista_conteudo.item(row)
					widget = self.parent.lista_conteudo.itemWidget(itens)
					if self.nome == widget.nome and self.local_json == widget.local_json:
						self.parent.lista_conteudo.takeItem(row)
						TOTAL_DESENHO = TOTAL_DESENHO - 1
						self.parent.rotulo_pesquisas.setText(self.tr(u"Meus Desenhos - ") + str(TOTAL_DESENHO))
						break
					else:
						...
			else:
				...
		except OSError as e:
			msg = Mensagem(self, QMessageBox.Critical, self.tr(u"Erro ao excluir: ") + str(e), u"Erro", QMessageBox.Ok)
			msg.exec()

	def ac_exportar(self):
		fileName, _ = QFileDialog.getSaveFileName(self, "Salvar coordenadas em", self.nome, "Arquivo clines bytes (*.clines);;Arquivo Texto (*.txt)")
		if fileName:
			if fileName.endswith(".clines"):
				with open(self.local_lines, "rb") as abrir:
					self.pts_exportar = load(abrir)

				with open(fileName, "wb") as salvar_linhas:
					dump(self.pts_exportar, salvar_linhas)
			elif fileName.endswith(".txt"):

				with open(self.local_lines, "rb") as abrir:
					self.pts_exportar = str(load(abrir))

				with open(fileName, "w") as salvar:
					salvar.write(self.pts_exportar)

	def diferenca(self, ponto_m1, ponto_m2):
		return sqrt((ponto_m1[0] - ponto_m2[0])**2 + (ponto_m1[1] - ponto_m2[1])**2)

	def ac_iniciar_desenho(self):
		global GET_NOME
		global GET_SVG
		global GET_LINHAS
		global GET_PONTOS

		GET_SVG = self.local_svg
		GET_LINHAS = self.local_lines
		GET_NOME = self.nome 
		GET_PONTOS = self.pontos

		# EXIBE MENSAGEM DE AVISO SE TIVER ATIVADO

		if CONFIG_AVISO != True:
			l1 = self.tr(u"<html><head/><body><p align=\"center\"><span style=\" font-size:11pt; font-weight:700;\">Atenção leia antes de desenhar</span><br/></p><p align=\"center\">Ao continuar o CamelTrace tem controle do mouse e apenas irá fazer o movimento do desenho</p><p align=\"center\">Para evitar estrago em seu computador certifique que o tamanho do desenho configurado é proporcional a sua tela e o local a ser desenhado</p><p align=\"center\">Recomendo fazer o teste no MsPaint do Windows.</p><p align=\"center\"><span style=\" font-size:10pt; font-style:italic;\">Lembra-se das </span><span style=\" font-size:10pt; font-weight:700; font-style:italic;\">Teclas de Atalho</span><span style=\" font-size:10pt; font-style:italic;\"> também pode ser configurado nas configurações</span></p>")
			l2 = self.tr(u"<p align=\"center\"><span style=\" font-size:14pt; font-weight:700; color:#55aa00;\">Tecla Iniciar: ") + str(CONFIG_ATALHO_INICIAR) + u"</span></p>"
			l3 = self.tr(u"<p align=\"center\"><span style=\" font-size:14pt; font-weight:700; color:#ff0000;\">Tecla Parar: ") + str(CONFIG_ATALHO_PARAR) + u"</span></p>"
			l4 = self.tr(u"<p align=\"center\"><span style=\" font-size:14pt; font-weight:700; color:#3079d6;\">Tecla Pausar: ") + str(CONFIG_ATALHO_PAUSAR) + u"</span></p></body></html>"
			msg = Mensagem(self, QMessageBox.Warning, f"{l1}{l2}{l3}{l4}", self.tr("Atenção"), QMessageBox.Ok)
			msg.exec()

		# MINIMIZA CAMELTRACE
		self.parent.setEnabled(False)
		self.parent.showMinimized()

		# CRIA UM SINAL ACESSIVEL PELA THREAD, ABAIXO

		self.pre_visualizar = CamelPreSvg()
		self.pre_visualizar.fechar.connect(self.pre_visualizar.close)

		# INICIA THREAD ALVO AC_OBTER_POS OBTEM A POSICAO DO MOUSE APOS O BREAK DO LOOP 

		self.thread_desenho = threading.Thread(target=self.ac_obter_pos)
		self.thread_desenho.daemon = True
		self.thread_desenho.start()

	def ac_obter_pos(self):
		parar = False

		# LOOP
		# SE A TECLA [?] FOI PRESSIONADA CANCELA O DESENHO OU INICIA
		# POSICOES XPOS YPOS
		# FECHA

		while True:
			if parar == True:
				break

			if keyboard.is_pressed(CONFIG_ATALHO_INICIAR):
				try:
					parar = True
					self.pre_visualizar.fechar.emit()
					self.ac_iniciar(XPOS, YPOS)
				except Exception as e:
					self.pre_visualizar.fechar.emit()
				finally:
					self.parent.setEnabled(True)
					self.parent.showNormal()
			if keyboard.is_pressed(CONFIG_ATALHO_PARAR):
				self.parent.showNormal()
				self.pre_visualizar.fechar.emit()
				self.parent.setEnabled(True)
				break

			time.sleep(0.05)

	def ac_iniciar(self, x, y):

		if not CONFIG_TEMPO_ESPERA[1] == False:
			time.sleep(CONFIG_TEMPO_ESPERA[0])

		# ABRE E LER ARQUIVO LINHAS DA VARIAVEL LOCAL GLOBAL

		with open(GET_LINHAS, "rb") as abrir:
			self.pts = load(abrir)

		# INICIA O TEMPO DO INICIO DO DESENHO
		# DESENHA
		# SE INICIADO - SEGURE O BOTAO ESQUERDO DO MOUSE
		# SE PAUSADO - SALVA O LOCAL X, Y - PAUSA O DESENHO
		# SE CANCELADO - NAO ALTERAR O TEMPO ESTIMADO

		cancelado = False
		self.rotulo_estimado.setText(u"  ")
		inicio = time.time()

		for self.pt in self.pts:
			iniciado = False
			pausado = False
			for i in range(0, len(self.pt) - 1):
				if self.diferenca(self.pt[i], self.pt[i - 1]) > 6 or pausado == True:
					pausado = False
					pyautogui.mouseUp()
					pyautogui.moveTo(self.pt[i][0] + x, self.pt[i][1] + y, 0)
					time.sleep(0.01)
					pyautogui.mouseDown()
				else:
					pyautogui.moveTo(self.pt[i][0] + x, self.pt[i][1] + y, 0)
				if not iniciado:
					iniciado = True
					pyautogui.mouseDown()
					time.sleep(0.01)
				if keyboard.is_pressed(CONFIG_ATALHO_PARAR):
					cancelado = True
					break
				if keyboard.is_pressed(CONFIG_ATALHO_PAUSAR):
					pyautogui.mouseUp()
					time.sleep(0.01)
					while True:
						if keyboard.is_pressed(CONFIG_ATALHO_INICIAR):
							pausado = True
							break
						time.sleep(0.05)

			pyautogui.mouseUp()
			time.sleep(0.20)

		if not cancelado:
			self.tempo_desenho = time.time() - inicio
			self.tempo_desenho = time.strftime("%H:%M:%S", time.gmtime(self.tempo_desenho))
			EditarJson(self.local_json, "Tempo", self.tempo_desenho)
			self.rotulo_estimado.setText(self.tr(u"Tempo Estimado: ") + str(self.tempo_desenho))

		if CONFIG_OTIMIZAR == True:
			liberar_memoria()

class CamelConfigKey(QKeySequenceEdit):
	def keyPressEvent(self, event):
		super().keyPressEvent(event)

		string = self.keySequence().toString(QKeySequence.NativeText)
		if string:
			ultimo_key = string.split(',')[-1].strip()
			self.setKeySequence(QKeySequence(ultimo_key))
	def obter(self):
		sequence = self.keySequence()
		string = sequence.toString(QKeySequence.NativeText)
		if string:
			return string
		else:
			return None

class CamelConfig(QDialog):
	def __init__(self, parent):
		super().__init__(parent)

		# DIALOG FILHO - ALINHADO NO CENTRO DA CLASS MAE CAMELTRACE

		self.parent = parent
		self.iscor = False
		self.lista_aguarda_tempo = ([(self.tr(u"Nenhum"), [False, 0]), (self.tr(u"1 Segundo"), [1, 1]), (self.tr(u"3 Segundos"), [3, 2]), (self.tr(u"5 Segundos"), [5, 3]), (self.tr(u"10 Segundos"), [10, 4]), (self.tr(u"30 Segundos"), [30, 5]), (self.tr(u"60 Segundos"), [60, 6]), ])
		self.lista_temas = ([(self.tr(u"Claro"), ["Light", 0]), (self.tr(u"Escuro"), ["Dark", 1]), ])


		self.setObjectName(u"CamelConfig")
		self.setWindowTitle(self.tr(u"Configurações"))
		self.setMinimumSize(QSize(500, 0))
		self.setSizeGripEnabled(True)
		self.setModal(True)
		self.verticalLayout = QVBoxLayout(self)
		self.verticalLayout.setObjectName(u"verticalLayout")
		self.tab_config = QTabWidget(self)
		self.tab_config.setObjectName(u"tab_config")
		self.tabela_config_geral = QWidget()
		self.tabela_config_geral.setObjectName(u"tabela_config_geral")
		self.verticalLayout_2 = QVBoxLayout(self.tabela_config_geral)
		self.verticalLayout_2.setObjectName(u"verticalLayout_2")
		self.frame_3 = QFrame(self.tabela_config_geral)
		self.frame_3.setObjectName(u"frame_3")
		self.gridLayout_3 = QGridLayout(self.frame_3)
		self.gridLayout_3.setObjectName(u"gridLayout_3")
		self.rotulo_titulo_cg = QLabel(self.frame_3)
		self.rotulo_titulo_cg.setObjectName(u"rotulo_titulo_cg")
		self.rotulo_titulo_cg.setAlignment(Qt.AlignCenter)
		self.gridLayout_3.addWidget(self.rotulo_titulo_cg, 0, 0, 1, 2)
		self.label_11 = QLabel(self.frame_3)
		self.label_11.setObjectName(u"label_11")
		self.gridLayout_3.addWidget(self.label_11, 4, 1, 1, 1)
		self.input_atalho_pausar = CamelConfigKey(self.frame_3)
		self.input_atalho_pausar.setObjectName(u"input_atalho_pausar")
		self.input_atalho_pausar.setMinimumSize(QSize(180, 25))
		self.input_atalho_pausar.setMaximumSize(QSize(180, 25))
		self.gridLayout_3.addWidget(self.input_atalho_pausar, 7, 1, 1, 1)
		self.input3 = QDoubleSpinBox(self.frame_3)
		self.input3.setObjectName(u"input3")
		self.input3.setMinimumSize(QSize(180, 25))
		self.input3.setMaximumSize(QSize(180, 25))
		self.input3.setAccelerated(True)
		self.input3.setDecimals(3)
		self.input3.setMinimum(0.001000000000000)
		self.input3.setMaximum(3.000000000000000)
		self.input3.setSingleStep(0.001000000000000)
		self.input3.setValue(0.003000000000000)
		self.gridLayout_3.addWidget(self.input3, 3, 0, 1, 1, Qt.AlignLeft)
		self.input5 = Combo_Personalizado(self.frame_3)
		self.input5.setObjectName(u"input_5")
		self.input5.setMinimumSize(QSize(180, 25))
		self.input5.setMaximumSize(QSize(180, 25))

		for i, (texto, valor) in enumerate(self.lista_aguarda_tempo):
			self.input5.addItem(texto)
			self.input5.setItemData(i, valor)

		self.gridLayout_3.addWidget(self.input5, 7, 0, 1, 1, Qt.AlignLeft)
		self.input6 = QCheckBox(self.frame_3)
		self.input6.setObjectName(u"input6")
		self.gridLayout_3.addWidget(self.input6, 8, 0, 1, 2)
		self.input_atalho_iniciar = CamelConfigKey(self.frame_3)
		self.input_atalho_iniciar.setObjectName(u"input_atalho_iniciar")
		self.input_atalho_iniciar.setMinimumSize(QSize(180, 25))
		self.input_atalho_iniciar.setMaximumSize(QSize(180, 25))
		self.gridLayout_3.addWidget(self.input_atalho_iniciar, 3, 1, 1, 1)
		self.label_12 = QLabel(self.frame_3)
		self.label_12.setObjectName(u"label_12")
		self.gridLayout_3.addWidget(self.label_12, 6, 1, 1, 1)
		self.input_atalho_parar = CamelConfigKey(self.frame_3)
		self.input_atalho_parar.setObjectName(u"input_atalho_parar")
		self.input_atalho_parar.setMinimumSize(QSize(180, 25))
		self.input_atalho_parar.setMaximumSize(QSize(180, 25))
		self.gridLayout_3.addWidget(self.input_atalho_parar, 5, 1, 1, 1)
		self.label_9 = QLabel(self.frame_3)
		self.label_9.setObjectName(u"label_9")
		self.gridLayout_3.addWidget(self.label_9, 4, 0, 1, 1, Qt.AlignLeft)
		self.input4 = QPushButton(self.frame_3)
		self.input4.setObjectName(u"input4")
		sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(180)
		sizePolicy.setHeightForWidth(self.input4.sizePolicy().hasHeightForWidth())
		self.input4.setSizePolicy(sizePolicy)
		self.input4.setMinimumSize(QSize(180, 25))
		self.input4.setMaximumSize(QSize(180, 25))
		self.input4.setCursor(QCursor(Qt.PointingHandCursor))
		self.input4.setAutoDefault(False)
		self.gridLayout_3.addWidget(self.input4, 5, 0, 1, 1, Qt.AlignLeft)
		self.line = QFrame(self.frame_3)
		self.line.setObjectName(u"line")
		self.line.setFrameShadow(QFrame.Plain)
		self.line.setFrameShape(QFrame.HLine)
		self.gridLayout_3.addWidget(self.line, 1, 0, 1, 2)
		self.label_10 = QLabel(self.frame_3)
		self.label_10.setObjectName(u"label_10")
		self.gridLayout_3.addWidget(self.label_10, 2, 1, 1, 1)
		self.label = QLabel(self.frame_3)
		self.label.setObjectName(u"label")
		self.gridLayout_3.addWidget(self.label, 6, 0, 1, 1, Qt.AlignLeft)
		self.label_8 = QLabel(self.frame_3)
		self.label_8.setObjectName(u"label_8")
		self.gridLayout_3.addWidget(self.label_8, 2, 0, 1, 1, Qt.AlignLeft)
		self.input7 = QCheckBox(self.frame_3)
		self.input7.setObjectName(u"input7")
		self.gridLayout_3.addWidget(self.input7, 9, 0, 1, 2)
		self.verticalLayout_2.addWidget(self.frame_3, 0, Qt.AlignTop)
		self.tab_config.addTab(self.tabela_config_geral, "")
		self.tabela_config_gui = QWidget()
		self.tabela_config_gui.setObjectName(u"tabela_config_gui")
		self.verticalLayout_3 = QVBoxLayout(self.tabela_config_gui)
		self.verticalLayout_3.setObjectName(u"verticalLayout_3")
		self.frame_4 = QFrame(self.tabela_config_gui)
		self.frame_4.setObjectName(u"frame_4")
		self.gridLayout_4 = QGridLayout(self.frame_4)
		self.gridLayout_4.setObjectName(u"gridLayout_4")

		self.input1 = Combo_Personalizado(self.frame_4)
		self.input1.setObjectName(u"input1")
		self.input1.setMinimumSize(QSize(180, 25))
		self.input1.setMaximumSize(QSize(180, 25))

		for i, (texto, valor) in enumerate(self.lista_temas):
			self.input1.addItem(texto)
			self.input1.setItemData(i, valor)

		self.gridLayout_4.addWidget(self.input1, 3, 0, 1, 1, Qt.AlignLeft)
		self.line_1 = QFrame(self.frame_4)
		self.line_1.setObjectName(u"line_1")
		self.line_1.setFrameShadow(QFrame.Plain)
		self.line_1.setFrameShape(QFrame.HLine)
		self.gridLayout_4.addWidget(self.line_1, 1, 0, 1, 2)
		self.label_3 = QLabel(self.frame_4)
		self.label_3.setObjectName(u"label_3")
		self.gridLayout_4.addWidget(self.label_3, 2, 0, 1, 1, Qt.AlignLeft)
		self.rotulo_titulo_cgg = QLabel(self.frame_4)
		self.rotulo_titulo_cgg.setObjectName(u"rotulo_titulo_cgg")
		self.rotulo_titulo_cgg.setAlignment(Qt.AlignCenter)
		self.rotulo_titulo_cgg.setWordWrap(True)
		self.gridLayout_4.addWidget(self.rotulo_titulo_cgg, 0, 0, 1, 2)
		self.verticalLayout_3.addWidget(self.frame_4, 0, Qt.AlignTop)
		self.tab_config.addTab(self.tabela_config_gui, "")
		self.verticalLayout.addWidget(self.tab_config)
		self.frame = QFrame(self)
		self.frame.setObjectName(u"frame")
		self.horizontalLayout = QHBoxLayout(self.frame)
		self.horizontalLayout.setObjectName(u"horizontalLayout")
		self.btn_cancelar = QPushButton(self.frame)
		self.btn_cancelar.setObjectName(u"btn_cancelar")
		self.btn_cancelar.setMinimumSize(QSize(120, 25))
		self.btn_cancelar.setMaximumSize(QSize(16777215, 25))
		self.btn_cancelar.setCursor(QCursor(Qt.PointingHandCursor))
		self.horizontalLayout.addWidget(self.btn_cancelar)
		self.btn_restaurar = QPushButton(self.frame)
		self.btn_restaurar.setObjectName(u"btn_restaurar")
		self.btn_restaurar.setMinimumSize(QSize(120, 25))
		self.btn_restaurar.setMaximumSize(QSize(16777215, 25))
		self.btn_restaurar.setCursor(QCursor(Qt.PointingHandCursor))
		self.horizontalLayout.addWidget(self.btn_restaurar)
		self.btn_salvar = QPushButton(self.frame)
		self.btn_salvar.setObjectName(u"btn_salvar")
		self.btn_salvar.setMinimumSize(QSize(120, 25))
		self.btn_salvar.setMaximumSize(QSize(16777215, 25))
		self.btn_salvar.setCursor(QCursor(Qt.PointingHandCursor))
		self.horizontalLayout.addWidget(self.btn_salvar)
		self.verticalLayout.addWidget(self.frame)

		self.retranslateUi()
		self.initConfig()

		self.tab_config.setCurrentIndex(0)
		self.btn_salvar.setDefault(True)
		self.input4.clicked.connect(self.ac_alterar_borda)
		self.btn_salvar.clicked.connect(self.ac_salvar_config)
		self.btn_restaurar.clicked.connect(self.ac_restaurar_padrao)
		self.btn_cancelar.clicked.connect(self.reject)
		#self.input5.currentIndexChanged.connect(self.teste)
		QMetaObject.connectSlotsByName(self)

		self.exec()

	def retranslateUi(self):
		self.rotulo_titulo_cg.setText(self.tr(u"Configuração Geral"))
		self.label_11.setText(self.tr(u"Tecla de Atalho: Parar o desenho"))
		self.input_atalho_pausar.setKeySequence(self.tr(u"Ctrl+Shift+J"))

		self.input6.setText(self.tr(u"Liberar memória automaticamente"))
		self.input_atalho_iniciar.setKeySequence(self.tr(u"Ctrl+B"))
		self.label_12.setText(self.tr(u"Tecla de Atalho: Pausar o desenho"))
		self.input_atalho_parar.setKeySequence(self.tr(u"Ctrl+L"))
		self.label_9.setText(self.tr(u"Cor da linha de borda visualização"))
		self.label_10.setText(self.tr(u"Tecla de Atalho: Iniciar o desenho"))
		self.label.setText(self.tr(u"Esperar alguns segundos antes de desenhar"))
		self.label_8.setText(self.tr(u"Tempo de pausa do mouse"))
		self.input7.setText(self.tr(u"Desativar mensagem de aviso ao desenhar"))
		self.tab_config.setTabText(self.tab_config.indexOf(self.tabela_config_geral), self.tr(u"Configuração Geral"))
		self.label_3.setText(self.tr(u"Tempo de pausa do mouse"))
		self.rotulo_titulo_cgg.setText(self.tr(u"Configuração Gui"))
		self.tab_config.setTabText(self.tab_config.indexOf(self.tabela_config_gui), self.tr(u"Configuração Gui"))
		self.btn_cancelar.setText(self.tr(u"Cancelar"))
		self.btn_restaurar.setText(self.tr(u"Restaurar Padrão"))
		self.btn_salvar.setText(self.tr(u"Salvar Alteração"))
	# retranslateUi

	@Slot()
	def initConfig(self):

		# INICIA TODAS AS CONFIGURAÇÕES SENDO ADICIONADA NA GUI DO CAMELTRACE CONFIGURACOES PELA VARIAVEL GLOBAL
		self.input1.setCurrentIndex(CONFIG_TEMA[1])
		self.input3.setValue(CONFIG_TEMPO_PAUSA)
		self.input4.setStyleSheet(f"#input4{{background-color: {CONFIG_COR_BORDA};}}")
		self.input7.setChecked(CONFIG_AVISO)
		self.input_atalho_iniciar.setKeySequence(f"{CONFIG_ATALHO_INICIAR}")
		self.input_atalho_parar.setKeySequence(f"{CONFIG_ATALHO_PARAR}")
		self.input_atalho_pausar.setKeySequence(f"{CONFIG_ATALHO_PAUSAR}")
		self.input5.setCurrentIndex(CONFIG_TEMPO_ESPERA[1])
		self.input6.setChecked(CONFIG_OTIMIZAR)

	def ac_alterar_borda(self):

		# OBTEM A COR DA BORDA USANDO QColorDialog.getColor
		# SE A COR FOR VALIDA RETORNA (Cor Selecionada)

		abrir_dialog = QColorDialog.getColor()
		if abrir_dialog.isValid():
			self.cor_borda = str(abrir_dialog.name(QColor.HexArgb))
			self.input4.setStyleSheet(f"#input4{{background-color: {self.cor_borda};}}")
			self.iscor = True

	def ac_salvar_config(self):

		global CONFIG_TEMA
		global CONFIG_AVISO
		global CONFIG_TEMPO_PAUSA
		global CONFIG_COR_BORDA
		global CONFIG_ATALHO_INICIAR
		global CONFIG_ATALHO_PARAR
		global CONFIG_ATALHO_PAUSAR
		global CONFIG_TEMPO_ESPERA
		global CONFIG_OTIMIZAR

		# SALVA AS CONFIGURAÇÕES

		EditarJson(LOCAL_CONFIG_JSON, 'Tema', self.input1.currentData())
		EditarJson(LOCAL_CONFIG_JSON, "Aviso", self.input7.isChecked())
		EditarJson(LOCAL_CONFIG_JSON, "Tempo_Pausa", self.input3.value())
		EditarJson(LOCAL_CONFIG_JSON, 'Tempo_Espera', self.input5.currentData())
		EditarJson(LOCAL_CONFIG_JSON, 'Auto_Otimizar', self.input6.isChecked())

		if self.input_atalho_iniciar.obter() == None or self.input_atalho_parar.obter() == None or self.input_atalho_pausar.obter() == None:
			msg = Mensagem(self, QMessageBox.Critical, self.tr(u"Erro campo tecla de atalho vazio"), self.tr(u"Campo Vazio"), QMessageBox.Ok)
			msg.exec()
		elif self.input_atalho_iniciar.obter() == self.input_atalho_parar.obter() or self.input_atalho_iniciar.obter() == self.input_atalho_pausar.obter():
			msg = Mensagem(self, QMessageBox.Critical, self.tr(u"Erro Teclas de atalho são iguais"), self.tr(u"Atalhos Iguais"), QMessageBox.Ok)
			msg.exec()
		elif self.input_atalho_parar.obter() == self.input_atalho_iniciar.obter() or self.input_atalho_parar.obter() == self.input_atalho_pausar.obter():
			msg = Mensagem(self, QMessageBox.Critical, self.tr(u"Erro Teclas de atalho são iguais"), self.tr(u"Atalhos Iguais"), QMessageBox.Ok)
			msg.exec()
		elif self.input_atalho_pausar.obter() == self.input_atalho_iniciar.obter() or self.input_atalho_pausar.obter() == self.input_atalho_parar.obter():
			msg = Mensagem(self, QMessageBox.Critical, self.tr(u"Erro Teclas de atalho são iguais"), self.tr(u"Atalhos Iguais"), QMessageBox.Ok)
			msg.exec()
		else:
			EditarJson(LOCAL_CONFIG_JSON, "Atalho_Iniciar", self.input_atalho_iniciar.obter())
			EditarJson(LOCAL_CONFIG_JSON, "Atalho_Parar", self.input_atalho_parar.obter())
			EditarJson(LOCAL_CONFIG_JSON, "Atalho_Pausar", self.input_atalho_pausar.obter())
			CONFIG_ATALHO_INICIAR = self.input_atalho_iniciar.obter()
			CONFIG_ATALHO_PARAR = self.input_atalho_parar.obter()
			CONFIG_ATALHO_PAUSAR = self.input_atalho_pausar.obter()

		if self.iscor == True:
			EditarJson(LOCAL_CONFIG_JSON, "Cor_Borda", self.cor_borda)
			CONFIG_COR_BORDA = self.cor_borda

		if CONFIG_TEMA != self.input1.currentData():
			reiniciar_cameltrace()

		CONFIG_AVISO = self.input7.isChecked()
		CONFIG_TEMPO_PAUSA = self.input3.value()
		CONFIG_TEMPO_ESPERA = self.input5.currentData()
		CONFIG_OTIMIZAR = self.input6.isChecked()
		pyautogui.PAUSE = self.input3.value()

		self.accept()

	def ac_restaurar_padrao(self):

		# RESTAURA CONFIGURACAO PADRAO

		restaurar = Criador_Config_Pasta()
		restaurar.ac_criar_config(False)

		self.accept()

class CamelView(QGraphicsView):
	def __init__(self):
		super().__init__()

		lista_argumentos = []

		self.primeira = True
		self.modo_visualizar = 1

		self.setScene(QGraphicsScene(self))
		self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
		self.setDragMode(QGraphicsView.ScrollHandDrag)
		self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
		self.setFundo()

	@Slot(str)
	def setFundo(self, entrada = "Xadrez"):

		# ADICIONA FUNDO DO CAMELVIEW

		if entrada == "Xadrez":
			xadrez_pix = QPixmap(64, 64)
			xadrez_pix.fill(Qt.white)
			xadrez_paint = QPainter(xadrez_pix)
			color = QColor(220, 220, 220)
			xadrez_paint.fillRect(0, 0, 32, 32, color)
			xadrez_paint.fillRect(32, 32, 32, 32, color)
			xadrez_paint.end()
			self.setBackgroundBrush(QBrush(xadrez_pix))
		else:
			self.setBackgroundBrush(QBrush(Qt.white, Qt.SolidPattern))

	def setVisualizar(self, visualizar):
		self.modo_visualizar = visualizar

	def setArgumentos(self, argumentos):
		global ARGUMENTOS
		self.lista_argumentos = argumentos
		ARGUMENTOS = " ".join(argumentos)

	@Slot(bool)
	def ac_abrir(self, entrada = False):
		if entrada == False:
			# LIMPAR CENA
			self.resetTransform()
			self.scene().clear()
			self.setScene(QGraphicsScene(self))
			self.ac_carregar_bmp()
		else:
			self.ac_carregar_svg()
			self.ac_visualizar_itens()

	@Slot()
	def ac_carregar_bmp(self):

		# ABRIR ARQUIVO BMP E ADICIONA PIXMAP NA CENA

		try:
			pixmap_bmp = QPixmap()
			pixmap_bmp.loadFromData(GLOBAL_BITMAP)

			self.visualizar_bmp = QGraphicsPixmapItem()
			self.visualizar_bmp.setPixmap(pixmap_bmp)
		except:
			self.visualizar_bmp = None

	@Slot()
	def ac_carregar_svg(self):

		# ABRIR ARQUIVO SVG E ADICIONA GRAFICO NA CENA E ATUALIZA OS ARGUMENTOS PASSADO

		global GLOBAL_SVG

		if GLOBAL_BITMAP is not None:
			argumentos_sub = ['potrace.exe'] + self.lista_argumentos + ["-s", "-", "-o-"]
			sub = subprocess.Popen(argumentos_sub, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
			GLOBAL_SVG, byt = sub.communicate(input=GLOBAL_BITMAP)

			try:
				string = GLOBAL_SVG.decode("utf-8").replace('\n', ' ').replace('fill="#000000" stroke="none"', 'fill="none" stroke="#000000"').replace('<path', '<path vector-effect="non-scaling-stroke"')
				self.svg_no_fill = bytes(string, encoding='utf-8')
			except:
				pass
				
			try:
				renderer = QSvgRenderer()

				self.visualizar_svg = QGraphicsSvgItem()
				self.visualizar_svg.setSharedRenderer(renderer)
				self.visualizar_svg.renderer().load(GLOBAL_SVG)
				self.visualizar_svg.setElementId("")
			except:
				self.visualizar_svg = None

			try:
				renderer_1 = QSvgRenderer()

				self.visualizar_svg_nofill = QGraphicsSvgItem()
				self.visualizar_svg_nofill.setSharedRenderer(renderer_1)
				self.visualizar_svg_nofill.renderer().load(self.svg_no_fill)
				self.visualizar_svg_nofill.setElementId("")
			except:
				self.visualizar_svg_nofill = None

	@Slot()
	def ac_visualizar_itens(self):

		for p in self.scene().items():
			self.scene().removeItem(p)

		if self.modo_visualizar == 0:
			if self.visualizar_bmp is not None:
				self.scene().addItem(self.visualizar_bmp)
		elif self.modo_visualizar == 1:
			if self.visualizar_svg is not None:
				self.scene().addItem(self.visualizar_svg)
		else:
			if self.visualizar_svg_nofill is not None:
				self.scene().addItem(self.visualizar_svg_nofill)
		if self.primeira == True:
			self.scale(0.50, 0.50)
			self.primeira = False

	def wheelEvent(self, oCQWheelEvent):
		fValue = 0
		fValue += oCQWheelEvent.angleDelta().x()
		fValue += oCQWheelEvent.angleDelta().y()
		fFactor = pow(1.2, fValue / 240.0)

		self.scale(fFactor, fFactor)

class CamelEditor(QMainWindow):
	def __init__(self, parent):
		super(CamelEditor, self).__init__(parent)

		self.parent = parent
		self.setObjectName(u"CamelTrace_Editor")
		self.lista_input_1 = ([(self.tr(u"Minoria"), "minority"), (self.tr(u"Maioria"), "majority"), (self.tr(u"Preto"), "black"), (self.tr(u"Branco"), "white"), (self.tr(u"Direita"), "right"), (self.tr(u"Esquerda"), "left"), (self.tr(u"Aleatório"), "random"), ])
		self.setWindowTitle("CamelTrace - Editor")
		self.setWindowModality(Qt.WindowModal)
		self.resize(900, 630)
		self.icone_cameltrace_editor = QIcon(u":/icones/Camellost_Azul_Logo.png")
		self.setWindowIcon(self.icone_cameltrace_editor)

		self.visualizador = CamelView()
		self.visualizador.setVisualizar(1)
		self.atualizar_argumentos_tempo = QTimer(self)

		icon1 = QIcon(u":/icones/Configurar.png")
		icon2 = QIcon(u":/icones/Mais-Zoom.png")
		icon3 = QIcon(u":/icones/Menos-Zoom.png")
		icon4 = QIcon(u":/icones/Visivel.png")
		icon5 = QIcon(u":/icones/Remove_Tinta.png")
		icon6 = QIcon(u":/icones/Bom.png")
		icon7 = QIcon(u":/icones/Ruim.png")
		icon8 = QIcon(u":/icones/Zoom-Padrao.png")
		icon9 = QIcon(u":/icones/Sobre.png")
		icon10 = QIcon(u":/icones/Xadrez.png")
		icon11 = QIcon(u":/icones/Exportar.png")

		self.actionVelocidade_atualizacao = QAction(self)
		self.actionVelocidade_atualizacao.setObjectName(u"actionVelocidade_atualizacao")
		self.actionVelocidade_atualizacao.setIcon(icon1)
		self.actionMais_Zoom = QAction(self)
		self.actionMais_Zoom.setObjectName(u"actionMais_Zoom")
		self.actionMais_Zoom.setIcon(icon2)
		self.actionMenos_Zoom = QAction(self)
		self.actionMenos_Zoom.setObjectName(u"actionMenos_Zoom")
		self.actionMenos_Zoom.setIcon(icon3)
		self.actionVisualizar_Bitmap = QAction(self)
		self.actionVisualizar_Bitmap.setObjectName(u"actionVisualizar_Bitmap")
		self.actionVisualizar_Bitmap.setCheckable(True)
		self.actionVisualizar_Bitmap.setIcon(icon4)
		self.actionVisualizar_Bitmap.setIconVisibleInMenu(False)
		self.actionPre_Visualizar = QAction(self)
		self.actionPre_Visualizar.setObjectName(u"actionPre_Visualizar")
		self.actionPre_Visualizar.setCheckable(True)
		self.actionPre_Visualizar.setIcon(icon5)
		self.actionPre_Visualizar.setIconVisibleInMenu(False)
		self.actionImagem_SVG = QAction(self)
		self.actionImagem_SVG.setObjectName(u"actionImagem_SVG")
		self.actionImagem_BMP = QAction(self)
		self.actionImagem_BMP.setObjectName(u"actionImagem_BMP")
		self.actionConcluido = QAction(self)
		self.actionConcluido.setObjectName(u"actionConcluido")
		self.actionConcluido.setIcon(icon6)
		self.actionCancelar = QAction(self)
		self.actionCancelar.setObjectName(u"actionCancelar")
		self.actionCancelar.setIcon(icon7)
		self.actionRestaurar_Zoom = QAction(self)
		self.actionRestaurar_Zoom.setObjectName(u"actionRestaurar_Zoom")
		self.actionRestaurar_Zoom.setIcon(icon8)
		self.actionSobre = QAction(self)
		self.actionSobre.setObjectName(u"actionSobre")
		self.actionSobre.setIcon(icon9)
		self.actionFundo_Branco = QAction(self)
		self.actionFundo_Branco.setObjectName(u"actionFundo_Branco")
		self.actionFundo_Branco.setCheckable(True)
		self.actionFundo_Branco.setIcon(icon10)
		self.actionFundo_Branco.setIconVisibleInMenu(False)
		self.actionSobre_Qt = QAction(self)
		self.actionSobre_Qt.setObjectName(u"actionSobre_Qt")
		self.centralwidget = QWidget(self)
		self.centralwidget.setObjectName(u"centralwidget")
		self.horizontalLayout = QHBoxLayout(self.centralwidget)
		self.horizontalLayout.setObjectName(u"horizontalLayout")
		self.splitter_2 = QSplitter(self.centralwidget)
		self.splitter_2.setObjectName(u"splitter_2")
		self.splitter_2.setOrientation(Qt.Horizontal)
		self.tela_editor = QFrame(self.splitter_2)
		self.tela_editor.setObjectName(u"tela_editor")
		self.tela_editor.setMaximumSize(QSize(320, 16777215))
		self.verticalLayout_21 = QVBoxLayout(self.tela_editor)
		self.verticalLayout_21.setObjectName(u"verticalLayout_21")
		self.logo_cameltrace = QPushButton(self.tela_editor)
		self.logo_cameltrace.setObjectName(u"logo_cameltrace")

		self.verticalLayout_21.addWidget(self.logo_cameltrace)

		self.line = QFrame(self.tela_editor)
		self.line.setObjectName(u"line")
		self.line.setFrameShadow(QFrame.Plain)
		self.line.setFrameShape(QFrame.HLine)

		self.verticalLayout_21.addWidget(self.line)

		self.scrollArea_6 = QScrollArea(self.tela_editor)
		self.scrollArea_6.setObjectName(u"scrollArea_6")
		self.scrollArea_6.setFrameShape(QFrame.NoFrame)
		self.scrollArea_6.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.scrollArea_6.setWidgetResizable(True)
		self.scroll_editor = QWidget()
		self.scroll_editor.setObjectName(u"scroll_editor")
		self.scroll_editor.setGeometry(QRect(0, 0, 302, 433))
		self.verticalLayout_22 = QVBoxLayout(self.scroll_editor)
		self.verticalLayout_22.setObjectName(u"verticalLayout_22")
		self.verticalLayout_22.setContentsMargins(0, 0, 0, 0)
		self.frame_14 = QFrame(self.scroll_editor)
		self.frame_14.setObjectName(u"frame_14")
		self.verticalLayout_23 = QVBoxLayout(self.frame_14)
		self.verticalLayout_23.setObjectName(u"verticalLayout_23")
		self.verticalLayout_23.setContentsMargins(0, 0, 0, 0)
		self.grupo_1 = QGroupBox(self.frame_14)
		self.grupo_1.setObjectName(u"grupo_1")
		sizePolicy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.grupo_1.sizePolicy().hasHeightForWidth())
		self.grupo_1.setSizePolicy(sizePolicy)
		self.gridLayout_4 = QGridLayout(self.grupo_1)
		self.gridLayout_4.setObjectName(u"gridLayout_4")
		self.input_2 = QSpinBox(self.grupo_1)
		self.input_2.setObjectName(u"input_2")
		self.input_2.setMinimumSize(QSize(128, 25))
		self.input_2.setFocusPolicy(Qt.WheelFocus)
		self.input_2.setValue(2)

		self.gridLayout_4.addWidget(self.input_2, 1, 1, 1, 1)

		self.input_4 = QDoubleSpinBox(self.grupo_1)
		self.input_4.setObjectName(u"input_4")
		self.input_4.setMinimumSize(QSize(128, 25))
		self.input_4.setDecimals(2)
		self.input_4.setMaximum(99.000000000000000)
		self.input_4.setSingleStep(0.100000000000000)
		self.input_4.setValue(0.200000000000000)

		self.gridLayout_4.addWidget(self.input_4, 3, 1, 1, 1)

		self.rotulo3 = QLabel(self.grupo_1)
		self.rotulo3.setObjectName(u"rotulo3")
		self.rotulo3.setWordWrap(True)

		self.gridLayout_4.addWidget(self.rotulo3, 2, 0, 1, 1)

		self.input_3 = QDoubleSpinBox(self.grupo_1)
		self.input_3.setObjectName(u"input_3")
		sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
		sizePolicy1.setHorizontalStretch(0)
		sizePolicy1.setVerticalStretch(0)
		sizePolicy1.setHeightForWidth(self.input_3.sizePolicy().hasHeightForWidth())
		self.input_3.setSizePolicy(sizePolicy1)
		self.input_3.setMinimumSize(QSize(128, 25))
		self.input_3.setMaximum(99.000000000000000)
		self.input_3.setSingleStep(0.100000000000000)
		self.input_3.setValue(1.000000000000000)

		self.gridLayout_4.addWidget(self.input_3, 2, 1, 1, 1)

		self.input_1 = Combo_Personalizado(self.grupo_1)

		for i, (texto, valor) in enumerate(self.lista_input_1):
			self.input_1.addItem(texto)
			self.input_1.setItemData(i, valor)

		self.input_1.setObjectName(u"input_1")
		sizePolicy1.setHeightForWidth(self.input_1.sizePolicy().hasHeightForWidth())
		self.input_1.setSizePolicy(sizePolicy1)
		self.input_1.setMinimumSize(QSize(128, 25))

		self.gridLayout_4.addWidget(self.input_1, 0, 1, 1, 1)

		self.rotulo1 = QLabel(self.grupo_1)
		self.rotulo1.setObjectName(u"rotulo1")
		self.rotulo1.setWordWrap(True)

		self.gridLayout_4.addWidget(self.rotulo1, 0, 0, 1, 1)

		self.rotulo4 = QLabel(self.grupo_1)
		self.rotulo4.setObjectName(u"rotulo4")
		self.rotulo4.setWordWrap(True)

		self.gridLayout_4.addWidget(self.rotulo4, 3, 0, 1, 1)

		self.rotulo2 = QLabel(self.grupo_1)
		self.rotulo2.setObjectName(u"rotulo2")
		self.rotulo2.setWordWrap(True)

		self.gridLayout_4.addWidget(self.rotulo2, 1, 0, 1, 1)

		self.input_5 = QCheckBox(self.grupo_1)
		self.input_5.setObjectName(u"input_5")
		sizePolicy2 = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
		sizePolicy2.setHorizontalStretch(0)
		sizePolicy2.setVerticalStretch(0)
		sizePolicy2.setHeightForWidth(self.input_5.sizePolicy().hasHeightForWidth())
		self.input_5.setSizePolicy(sizePolicy2)

		self.gridLayout_4.addWidget(self.input_5, 4, 0, 1, 2)


		self.verticalLayout_23.addWidget(self.grupo_1)

		self.grupo_2 = QGroupBox(self.frame_14)
		self.grupo_2.setObjectName(u"grupo_2")
		sizePolicy.setHeightForWidth(self.grupo_2.sizePolicy().hasHeightForWidth())
		self.grupo_2.setSizePolicy(sizePolicy)
		self.gridLayout_5 = QGridLayout(self.grupo_2)
		self.gridLayout_5.setObjectName(u"gridLayout_5")
		self.rotulo5 = QLabel(self.grupo_2)
		self.rotulo5.setObjectName(u"rotulo5")
		self.rotulo5.setWordWrap(True)

		self.gridLayout_5.addWidget(self.rotulo5, 0, 0, 1, 1)

		self.input_6 = QDoubleSpinBox(self.grupo_2)
		self.input_6.setObjectName(u"input_6")
		self.input_6.setMinimumSize(QSize(128, 25))
		self.input_6.setMinimum(0.000000000000000)
		self.input_6.setMaximum(0.990000000000000)
		self.input_6.setSingleStep(0.050000000000000)
		self.input_6.setValue(0.500000000000000)

		self.gridLayout_5.addWidget(self.input_6, 0, 1, 1, 1)

		self.input_7 = QCheckBox(self.grupo_2)
		self.input_7.setObjectName(u"input_7")
		self.input_7.setMinimumSize(QSize(128, 0))

		self.gridLayout_5.addWidget(self.input_7, 1, 0, 1, 2)

		self.input_8 = QCheckBox(self.grupo_2)
		self.input_8.setObjectName(u"input_8")
		self.input_8.setMinimumSize(QSize(128, 0))

		self.gridLayout_5.addWidget(self.input_8, 2, 0, 1, 2)


		self.verticalLayout_23.addWidget(self.grupo_2)


		self.verticalLayout_22.addWidget(self.frame_14, 0, Qt.AlignTop)

		self.scrollArea_6.setWidget(self.scroll_editor)

		self.verticalLayout_21.addWidget(self.scrollArea_6)

		self.splitter_2.addWidget(self.tela_editor)
		self.visualizador.ac_abrir()
		self.ac_atualizar_argumentos()
		self.tela_visualizador = QWidget(self.splitter_2)
		self.tela_visualizador.setObjectName(u"tela_visualizador")
		self.verticalLayout_4 = QVBoxLayout(self.tela_visualizador)
		self.verticalLayout_4.setObjectName(u"verticalLayout_4")
		self.verticalLayout_4.addWidget(self.visualizador)
		self.splitter_2.addWidget(self.tela_visualizador)

		self.horizontalLayout.addWidget(self.splitter_2)

		self.setCentralWidget(self.centralwidget)
		self.menubar = QMenuBar(self)
		self.menubar.setObjectName(u"menubar")
		self.menubar.setGeometry(QRect(0, 0, 900, 57))
		self.menuArquivo = Menu_Personalizado(self.menubar)
		self.menuArquivo.setObjectName(u"menuArquivo")
		self.menuExportar = Menu_Personalizado(self.menuArquivo)
		self.menuExportar.setObjectName(u"menuExportar")
		self.menuExportar.setIcon(icon11)
		self.menuExibir = Menu_Personalizado(self.menubar)
		self.menuExibir.setObjectName(u"menuExibir")
		self.menuOpcoes = Menu_Personalizado(self.menubar)
		self.menuOpcoes.setObjectName(u"menuOpcoes")
		self.menuAjuda = Menu_Personalizado(self.menubar)
		self.menuAjuda.setObjectName(u"menuAjuda")
		self.setMenuBar(self.menubar)
		self.barra_estado = QStatusBar(self)
		self.barra_estado.setObjectName(u"barra_estado")
		self.setStatusBar(self.barra_estado)
		self.barra_ferramenta_1 = QToolBar(self)
		self.barra_ferramenta_1.setObjectName(u"barra_ferramenta_1")
		self.barra_ferramenta_1.setMinimumSize(QSize(0, 48))
		self.barra_ferramenta_1.setMovable(False)
		self.barra_ferramenta_1.setAllowedAreas(Qt.NoToolBarArea)
		self.addToolBar(Qt.TopToolBarArea, self.barra_ferramenta_1)
		self.barra_ferramenta_2 = QToolBar(self)
		self.barra_ferramenta_2.setObjectName(u"barra_ferramenta_2")
		self.barra_ferramenta_2.setAllowedAreas(Qt.TopToolBarArea)
		self.barra_ferramenta_2.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
		self.addToolBar(Qt.TopToolBarArea, self.barra_ferramenta_2)

		self.menubar.addAction(self.menuArquivo.menuAction())
		self.menubar.addAction(self.menuExibir.menuAction())
		self.menubar.addAction(self.menuOpcoes.menuAction())
		self.menubar.addAction(self.menuAjuda.menuAction())
		self.menuArquivo.addAction(self.actionConcluido)
		self.menuArquivo.addAction(self.menuExportar.menuAction())
		self.menuArquivo.addSeparator()
		self.menuArquivo.addAction(self.actionCancelar)
		self.menuExportar.addAction(self.actionImagem_SVG)
		self.menuExportar.addAction(self.actionImagem_BMP)
		self.menuExibir.addAction(self.actionVisualizar_Bitmap)
		self.menuExibir.addAction(self.actionPre_Visualizar)
		self.menuExibir.addAction(self.actionFundo_Branco)
		self.menuExibir.addSeparator()
		self.menuExibir.addAction(self.actionRestaurar_Zoom)
		self.menuExibir.addAction(self.actionMais_Zoom)
		self.menuExibir.addAction(self.actionMenos_Zoom)
		self.menuOpcoes.addAction(self.actionVelocidade_atualizacao)
		self.menuAjuda.addAction(self.actionSobre)
		self.menuAjuda.addAction(self.actionSobre_Qt)
		self.barra_ferramenta_1.addAction(self.actionMais_Zoom)
		self.barra_ferramenta_1.addAction(self.actionMenos_Zoom)
		self.barra_ferramenta_1.addAction(self.actionRestaurar_Zoom)
		self.barra_ferramenta_1.addSeparator()
		self.barra_ferramenta_1.addAction(self.actionVisualizar_Bitmap)
		self.barra_ferramenta_1.addAction(self.actionPre_Visualizar)
		self.barra_ferramenta_1.addAction(self.actionFundo_Branco)
		self.barra_ferramenta_1.addSeparator()
		self.barra_ferramenta_2.addAction(self.actionCancelar)
		self.barra_ferramenta_2.addAction(self.actionConcluido)


		self.retranslateUi()

		self.atualizar_argumentos_tempo.timeout.connect(lambda: self.visualizador.ac_abrir(1))
		self.actionMais_Zoom.triggered.connect(self.ac_mais_zoom)
		self.actionMenos_Zoom.triggered.connect(self.ac_menos_zoom)
		self.actionRestaurar_Zoom.triggered.connect(self.ac_normal_zoom)
		self.actionVisualizar_Bitmap.triggered.connect(lambda: self.ac_alterar_visualizar(self.actionVisualizar_Bitmap.isChecked()))
		self.actionPre_Visualizar.triggered.connect(lambda: self.ac_alterar_visualizar_pre(self.actionPre_Visualizar.isChecked()))
		self.actionFundo_Branco.triggered.connect(lambda: self.ac_alterar_fundo(self.actionFundo_Branco.isChecked()))
		self.actionVelocidade_atualizacao.triggered.connect(self.ac_opcoes)
		self.actionCancelar.triggered.connect(self.close)
		self.actionConcluido.triggered.connect(self.ac_concluido)
		self.actionImagem_SVG.triggered.connect(self.ac_salvar_svg)
		self.actionImagem_BMP.triggered.connect(self.ac_salvar_bmp)
		self.actionSobre.triggered.connect(self.ac_sobre_cameleditor)
		self.actionSobre_Qt.triggered.connect(qApp.aboutQt)

		self.input_1.currentIndexChanged.connect(self.currentIndexChanged)
		self.input_2.valueChanged.connect(self.valueChanged)
		self.input_3.valueChanged.connect(self.valueChanged)
		self.input_4.valueChanged.connect(self.valueChanged)
		self.input_5.stateChanged.connect(self.stateChanged)
		self.input_6.valueChanged.connect(self.valueChanged)
		self.input_7.stateChanged.connect(self.stateChanged)
		self.input_8.stateChanged.connect(self.stateChanged)

		self.input_1.setCurrentIndex(0)
		QMetaObject.connectSlotsByName(self)

		self.show()

	def retranslateUi(self):
		self.actionVelocidade_atualizacao.setText(self.tr(u"Opções"))
#if QT_CONFIG(statustip)
		self.actionVelocidade_atualizacao.setStatusTip(self.tr(u"Opções"))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(shortcut)
		self.actionVelocidade_atualizacao.setShortcut(self.tr(u"Ctrl+P"))
#endif // QT_CONFIG(shortcut)
		self.actionMais_Zoom.setText(self.tr(u"Mais Zoom"))
#if QT_CONFIG(statustip)
		self.actionMais_Zoom.setStatusTip(self.tr(u"Mais Zoom"))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(shortcut)
		self.actionMais_Zoom.setShortcut(self.tr(u"Alt+="))
#endif // QT_CONFIG(shortcut)
		self.actionMenos_Zoom.setText(self.tr(u"Menos Zoom"))
#if QT_CONFIG(statustip)
		self.actionMenos_Zoom.setStatusTip(self.tr(u"Menos Zoom"))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(shortcut)
		self.actionMenos_Zoom.setShortcut(self.tr(u"Alt+-"))
#endif // QT_CONFIG(shortcut)
		self.actionVisualizar_Bitmap.setText(self.tr(u"Visualizar Bitmap"))
#if QT_CONFIG(statustip)
		self.actionVisualizar_Bitmap.setStatusTip(self.tr(u"Visualizar Bitmap"))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(shortcut)
		self.actionVisualizar_Bitmap.setShortcut(self.tr(u"Ctrl+B"))
#endif // QT_CONFIG(shortcut)
		self.actionPre_Visualizar.setText(self.tr(u"Pré-Visualizar"))
#if QT_CONFIG(tooltip)
		self.actionPre_Visualizar.setToolTip(self.tr(u"Pré-Visualização do desenho final"))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
		self.actionPre_Visualizar.setStatusTip(self.tr(u"Pré-Visualização do desenho final"))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(shortcut)
		self.actionPre_Visualizar.setShortcut(self.tr(u"Alt+P"))
#endif // QT_CONFIG(shortcut)
		self.actionImagem_SVG.setText(self.tr(u"Imagem SVG"))
		self.actionImagem_BMP.setText(self.tr(u"Imagem BMP"))
		self.actionConcluido.setText(self.tr(u"Concluido"))
#if QT_CONFIG(tooltip)
		self.actionConcluido.setToolTip(self.tr(u"Salvar Alterações (Ctrl+S)"))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
		self.actionConcluido.setStatusTip(self.tr(u"Salva as alterações do svg"))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(shortcut)
		self.actionConcluido.setShortcut(self.tr(u"Ctrl+S"))
#endif // QT_CONFIG(shortcut)
		self.actionCancelar.setText(self.tr(u"Cancelar"))
#if QT_CONFIG(tooltip)
		self.actionCancelar.setToolTip(self.tr(u"Cancelar Alterações  (Ctrl+W)"))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
		self.actionCancelar.setStatusTip(self.tr(u"Cancela todas as alterações feitas"))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(shortcut)
		self.actionCancelar.setShortcut(self.tr(u"Ctrl+W"))
#endif // QT_CONFIG(shortcut)
		self.actionRestaurar_Zoom.setText(self.tr(u"Restaurar Zoom"))
#if QT_CONFIG(statustip)
		self.actionRestaurar_Zoom.setStatusTip(self.tr(u"Restaurar Zoom"))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(shortcut)
		self.actionRestaurar_Zoom.setShortcut(self.tr(u"Alt+0"))
#endif // QT_CONFIG(shortcut)
		self.actionSobre.setText(self.tr(u"Sobre"))
#if QT_CONFIG(statustip)
		self.actionSobre.setStatusTip(self.tr(u"Sobre"))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(shortcut)
		self.actionSobre.setShortcut(self.tr(u"Ctrl+F1"))
#endif // QT_CONFIG(shortcut)
		self.actionFundo_Branco.setText(self.tr(u"Fundo Branco"))
#if QT_CONFIG(tooltip)
		self.actionFundo_Branco.setToolTip(self.tr(u"Fundo Branco Fundo Xadrez"))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
		self.actionFundo_Branco.setStatusTip(self.tr(u"Fundo Branco\\ Fundo Xadrez"))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(shortcut)
		self.actionFundo_Branco.setShortcut(self.tr(u"Ctrl+9"))
#endif // QT_CONFIG(shortcut)
		self.actionSobre_Qt.setText(self.tr(u"Sobre Qt"))
		self.grupo_1.setTitle(self.tr(u"Avançado"))
#if QT_CONFIG(tooltip)
		self.rotulo3.setToolTip(self.tr(u"Parâmetro de limite de canto (padrão 1)"))
#endif // QT_CONFIG(tooltip)
		self.rotulo3.setText(self.tr(u"Limite de Canto"))
#if QT_CONFIG(tooltip)
		self.rotulo1.setToolTip(self.tr(u"Como resolver ambiguidades na decomposição do caminho"))
#endif // QT_CONFIG(tooltip)
		self.rotulo1.setText(self.tr(u"Política de Retorno"))
#if QT_CONFIG(tooltip)
		self.rotulo4.setToolTip(self.tr(u"Tolerância de otimização de curva (padrão 0,2)"))
#endif // QT_CONFIG(tooltip)
		self.rotulo4.setText(self.tr(u"Tolerância de Otimização"))
#if QT_CONFIG(tooltip)
		self.rotulo2.setToolTip(self.tr(u"Suprime manchas de até este tamanho (padrão 2)"))
#endif // QT_CONFIG(tooltip)
		self.rotulo2.setText(self.tr(u"Tamanho do Esboço"))
		self.input_5.setText(self.tr(u"Desativa a otimização da curva"))
		self.grupo_2.setTitle(self.tr(u"Cores"))
#if QT_CONFIG(tooltip)
		self.rotulo5.setToolTip(self.tr(u"Corte preto/branco no arquivo de entrada (padrão 0,5)"))
#endif // QT_CONFIG(tooltip)
		self.rotulo5.setText(self.tr(u"Corte Preto/Branco"))
		self.input_7.setText(self.tr(u"Inverter Cor"))
		self.input_8.setText(self.tr(u"Remove o Espaço em Branco"))
		self.menuArquivo.setTitle(self.tr(u"Arquivo"))
		self.menuExportar.setTitle(self.tr(u"Exportar Imagem"))
		self.menuExibir.setTitle(self.tr(u"Exibir"))
		self.menuOpcoes.setTitle(self.tr(u"Opções"))
		self.menuAjuda.setTitle(self.tr(u"Ajuda"))
		self.barra_ferramenta_1.setWindowTitle(self.tr(u"Barra de Ferramentas"))
		self.barra_ferramenta_2.setWindowTitle(self.tr(u"Barra de Ferramentas 2"))
	# retranslateUi

	def ac_sobre_cameleditor(self):
		self.caixa_cameleditor = QDialog(self)
		self.caixa_cameleditor.setObjectName(u"Sobre_CamelEditor")
		self.caixa_cameleditor.setWindowTitle(self.tr(u"Sobre CamelEditor"))
		self.verticalLayout = QVBoxLayout(self.caixa_cameleditor)
		self.verticalLayout.setObjectName(u"verticalLayout")
		self.grupo_cameleditor = QGroupBox(self.caixa_cameleditor)
		self.grupo_cameleditor.setObjectName(u"grupo_cameleditor")
		self.grupo_cameleditor.setTitle(self.tr(u"CamelEditor"))
		self.verticalLayout_2 = QVBoxLayout(self.grupo_cameleditor)
		self.verticalLayout_2.setObjectName(u"verticalLayout_2")
		self.horizontalLayout = QHBoxLayout()
		self.horizontalLayout.setObjectName(u"horizontalLayout")
		self.logo_cameltrace_e = QPushButton(self.grupo_cameleditor)
		self.logo_cameltrace_e.setObjectName(u"logo_cameltrace_e")
		self.logo_cameltrace_e.setToolTip(self.tr(u"Logo CamelTrace"))
		self.horizontalLayout.addWidget(self.logo_cameltrace_e)
		self.label = QLabel(self.grupo_cameleditor)
		self.label.setObjectName(u"label")
		self.label.setWordWrap(True)
		self.label.setText(self.tr(u"Editor de svg para CamelTrace\n"
"Criador por: Emerson Maciel\n"
"Version: CamelTrace v2.12 - Camellost"))
		self.horizontalLayout.addWidget(self.label)
		self.verticalLayout_2.addLayout(self.horizontalLayout)
		self.horizontalLayout_2 = QHBoxLayout()
		self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
		self.logo_icons8_e = QPushButton(self.grupo_cameleditor)
		self.logo_icons8_e.setObjectName(u"logo_icons8_e")
		self.logo_icons8_e.setToolTip(self.tr(u"Logo Icons8"))
		self.horizontalLayout_2.addWidget(self.logo_icons8_e)
		self.label_2 = QLabel(self.grupo_cameleditor)
		self.label_2.setObjectName(u"label_2")
		self.label_2.setOpenExternalLinks(True)
		self.label_2.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)
		self.label_2.setText(self.tr(u"<html><head/><body><p>Agradecimento Ícones de <a href=\"https://icons8.com/\"><span style=\" text-decoration: underline; color:#3079d6;\">icons8.com</span></a></p></body></html>"))
		self.horizontalLayout_2.addWidget(self.label_2)
		self.verticalLayout_2.addLayout(self.horizontalLayout_2)
		self.verticalLayout.addWidget(self.grupo_cameleditor)
		self.grupo_potrace = QGroupBox(self.caixa_cameleditor)
		self.grupo_potrace.setObjectName(u"grupo_potrace")
		self.grupo_potrace.setMinimumSize(QSize(0, 0))
		self.grupo_potrace.setTitle(self.tr(u"Transformando bitmaps em graficos vetoriais "))
		self.horizontalLayout_15 = QHBoxLayout(self.grupo_potrace)
		self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
		self.logo_potrace_e = QPushButton(self.grupo_potrace)
		self.logo_potrace_e.setObjectName(u"logo_potrace_e")
		self.logo_potrace_e.setToolTip(self.tr(u"Logo potrace"))
		self.horizontalLayout_15.addWidget(self.logo_potrace_e)
		self.rotulo_sobre2 = QLabel(self.grupo_potrace)
		self.rotulo_sobre2.setObjectName(u"rotulo_sobre2")
		self.rotulo_sobre2.setCursor(QCursor(Qt.IBeamCursor))
		self.rotulo_sobre2.setOpenExternalLinks(True)
		self.rotulo_sobre2.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)
		self.rotulo_sobre2.setText(self.tr(u"<html><head/><body><p align=\"center\">Transforming bitmaps into vector graphics</p><p align=\"center\">Autor: Copyright © 2001-2017 Peter Selinger.</p><p align=\"center\">url: <a href=\"http://potrace.sourceforge.net\"><span style=\" font-size:10pt; text-decoration: underline; color:#3079d6;\">potrace.sourceforge.net</span></a></p><p>The Potrace logo and mascot was designed by Karol Krenski.</p><p>Copyright © 2003 Karol Krenski and Peter Selinger. The logo is licensed under GPL.</p></body></html>"))
		self.horizontalLayout_15.addWidget(self.rotulo_sobre2)
		self.verticalLayout.addWidget(self.grupo_potrace)
		self.buttonBox = QDialogButtonBox(self.caixa_cameleditor)
		self.buttonBox.setObjectName(u"buttonBox")
		self.buttonBox.setOrientation(Qt.Horizontal)
		self.buttonBox.setStandardButtons(QDialogButtonBox.Ok)
		self.verticalLayout.addWidget(self.buttonBox)

		self.buttonBox.accepted.connect(self.caixa_cameleditor.accept)
		self.buttonBox.rejected.connect(self.caixa_cameleditor.reject)

		QMetaObject.connectSlotsByName(self.caixa_cameleditor)

		self.caixa_cameleditor.exec()

	def ac_salvar_svg(self):

		fileName, _ = QFileDialog.getSaveFileName(self, "Salvar SVG em", "", "Arquivo Scalable Vector Graphics (*.svg)")
		if fileName:
			with open(fileName, "w") as abrir:
				abrir.write(GLOBAL_SVG.decode("utf-8").replace('\n', ' '))

	def ac_salvar_bmp(self):

		fileName, _ = QFileDialog.getSaveFileName(self, "Salvar BMP em", "", "Arquivo Bitmap (*.bmp)")
		if fileName:
			with open(fileName, "wb") as abrir:
				abrir.write(GLOBAL_BITMAP)

	def ac_opcoes(self):
		self.caixa_tempo = QDialog(self)
		self.caixa_tempo.setObjectName(u"caixa_tempo")
		self.caixa_tempo.setWindowTitle(self.tr(u"Opções"))
		self.verticalLayout = QVBoxLayout(self.caixa_tempo)
		self.verticalLayout.setObjectName(u"verticalLayout")
		self.label = QLabel(self.caixa_tempo)
		self.label.setObjectName(u"label")
		self.label.setText(self.tr(u"Tempo atualização dos argumentos"))
		self.verticalLayout.addWidget(self.label)
		self.input_9 = QSpinBox(self.caixa_tempo)
		self.input_9.setObjectName(u"input_9")
		self.input_9.setAccelerated(True)
		self.input_9.setMinimum(30)
		self.input_9.setMaximum(5000)
		self.input_9.setValue(int(CONFIG_TEMPO_ATUALIZAR))
		self.verticalLayout.addWidget(self.input_9)
		self.buttonBox = QDialogButtonBox(self.caixa_tempo)
		self.buttonBox.setObjectName(u"buttonBox")
		self.buttonBox.setOrientation(Qt.Horizontal)
		self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
		self.verticalLayout.addWidget(self.buttonBox)
		self.buttonBox.accepted.connect(self.ac_tempo_atualizar)
		self.buttonBox.rejected.connect(self.caixa_tempo.reject)

		QMetaObject.connectSlotsByName(self.caixa_tempo)

		self.caixa_tempo.exec()

	def ac_tempo_atualizar(self):

		# OPCOES CAMELEDITOR

		global CONFIG_TEMPO_ATUALIZAR

		if self.input_9.value():
			EditarJson(LOCAL_CONFIG_JSON, "Tempo_Atualizar", int(self.input_9.value()))
			CONFIG_TEMPO_ATUALIZAR = int(self.input_9.value())
		self.caixa_tempo.accept()

	def ac_concluido(self):

		# ACEITA ALTERACAO DO SVG
		if CONFIG_OTIMIZAR == True:
			liberar_memoria()
		self.parent.ac_temporario_3(GLOBAL_SVG)

		self.close()

	@Slot()
	def ac_atualizar_argumentos(self):

		# ATUALIZA ARGUMENTOS

		argumentos = []

		self.valor_Turn = self.input_1.currentData()

		if self.input_5.isChecked() == True:
			argumentos.append("--longcurve")
		if self.input_8.isChecked() == True:
			argumentos.append("--tight")
		if self.input_7.isChecked() == True:
			argumentos.append("--invert")

		argumentos.append("--turnpolicy=" + self.valor_Turn)
		argumentos.append("--turdsize=" + str(self.input_2.value()))
		argumentos.append("--alphamax=" + str(self.input_3.value()))
		argumentos.append("--opttolerance=" + str(self.input_4.value()))
		#argumentos.append("--unit=" + str(self.ptUnit.value()))
		argumentos.append("--blacklevel=" + str(self.input_6.value()))
		argumentos.append("--flat")

		self.visualizador.setArgumentos(argumentos)

		self.atualizar_argumentos_tempo.setSingleShot(True)
		self.atualizar_argumentos_tempo.start(CONFIG_TEMPO_ATUALIZAR)


	@Slot()
	def ac_normal_zoom(self):
		self.visualizador.resetTransform()
		self.visualizador.scale(0.50, 0.50)

	@Slot()
	def ac_mais_zoom(self):
		self.visualizador.scale(1.20, 1.20)

	@Slot()
	def ac_menos_zoom(self):
		self.visualizador.scale(0.80, 0.80)

	@Slot(bool)
	def ac_alterar_visualizar(self, entrada):
		if entrada is True:
			self.visualizador.setVisualizar(0)
		else:
			self.visualizador.setVisualizar(1)
		self.visualizador.ac_visualizar_itens()

	@Slot(bool)
	def ac_alterar_visualizar_pre(self, entrada):
		if entrada is True:
			self.visualizador.setVisualizar(2)
		else:
			self.visualizador.setVisualizar(1)
		self.visualizador.ac_visualizar_itens()

	@Slot(bool)
	def ac_alterar_fundo(self, entrada):
		if entrada is True:
			self.visualizador.setFundo('Branco')
		else:
			self.visualizador.setFundo('Xadrez')
	@Slot(float)		
	def currentIndexChanged(self, nIndex):
		self.ac_atualizar_argumentos()
	@Slot(int)	
	def valueChanged(self, nValue):
		self.ac_atualizar_argumentos()
	@Slot(float)	
	def stateChanged(self, nState):
		self.ac_atualizar_argumentos()

class CamelTrace(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setObjectName(u"CamelTrace")
		self.setWindowTitle("CamelTrace")
		self.resize(1081, 600)
		self.icone_cameltrace_window = QIcon(u":/icones/Camellost_Azul_Logo.png")
		self.setWindowIcon(self.icone_cameltrace_window)

		icon_grade = QIcon(u":/icones/Grade.png")
		icon_lista = QIcon(u":/icones/Fileira.png")

		menu_mode = Menu_Personalizado(self)
		self.actionMode_Grade = QAction(self)
		self.actionMode_Grade.setIcon(icon_grade)
		self.actionMode_Lista = QAction(self)
		self.actionMode_Lista.setIcon(icon_lista)
		self.actionMode_Grade.setText(self.tr(u"Modo Grade"))
		self.actionMode_Lista.setText(self.tr(u"Modo Fileira"))
		menu_mode.addAction(self.actionMode_Grade)
		menu_mode.addAction(self.actionMode_Lista)

		menu_opcoes = Menu_Personalizado(self)
		self.actionRemove_Imagem = QAction(self)
		self.actionRemove_Imagem.setCheckable(True)
		self.actionRemove_Imagem.setText(self.tr(u"Esconder Imagem do desenho"))
		self.actionCor_Fundo = QAction(self)
		self.actionCor_Fundo.setText(self.tr(u"Alterar cor do fundo"))
		menu_opcoes.addAction(self.actionRemove_Imagem)
		menu_opcoes.addAction(self.actionCor_Fundo)

		self.tela_central = QWidget(self)
		self.tela_central.setObjectName(u"tela_central")
		self.horizontalLayout = QHBoxLayout(self.tela_central)
		self.horizontalLayout.setObjectName(u"horizontalLayout")
		self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
		self.tela_menu = QFrame(self.tela_central)
		self.tela_menu.setObjectName(u"tela_menu")
		self.tela_menu.setMinimumSize(QSize(53, 0))
		self.tela_menu.setMaximumSize(QSize(220, 16777215))
		self.verticalLayout_15 = QVBoxLayout(self.tela_menu)
		self.verticalLayout_15.setObjectName(u"verticalLayout_15")
		self.logo_cameltrace = QPushButton(self.tela_menu)
		self.logo_cameltrace.setObjectName(u"logo_cameltrace")

		self.verticalLayout_15.addWidget(self.logo_cameltrace)

		self.verticalSpacer_2 = QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Fixed)

		self.verticalLayout_15.addItem(self.verticalSpacer_2)

		self.btn_menu1 = Botao_Personalizado(self.tela_menu, 0)
		self.btn_menu1.setAtivo(True)
		self.btn_menu1.setObjectName(u"btn_menu1")
		sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.btn_menu1.sizePolicy().hasHeightForWidth())
		self.btn_menu1.setSizePolicy(sizePolicy)
		self.btn_menu1.setMinimumSize(QSize(35, 35))
		self.btn_menu1.setMaximumSize(QSize(16777215, 35))
		self.btn_menu1.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

		self.btn_menu2 = Botao_Personalizado(self.tela_menu, 1)
		self.btn_menu2.setObjectName(u"btn_menu2")
		sizePolicy.setHeightForWidth(self.btn_menu2.sizePolicy().hasHeightForWidth())
		self.btn_menu2.setSizePolicy(sizePolicy)
		self.btn_menu2.setMinimumSize(QSize(35, 35))
		self.btn_menu2.setMaximumSize(QSize(16777215, 35))
		self.btn_menu2.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

		self.btn_menu3 = Botao_Personalizado(self.tela_menu, 2)
		self.btn_menu3.setObjectName(u"btn_menu3")
		sizePolicy.setHeightForWidth(self.btn_menu3.sizePolicy().hasHeightForWidth())
		self.btn_menu3.setSizePolicy(sizePolicy)
		self.btn_menu3.setMinimumSize(QSize(35, 35))
		self.btn_menu3.setMaximumSize(QSize(16777215, 35))
		self.btn_menu3.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

		self.btn_menu4 = Botao_Personalizado(self.tela_menu, 3)
		self.btn_menu4.setObjectName(u"btn_menu4")
		sizePolicy.setHeightForWidth(self.btn_menu4.sizePolicy().hasHeightForWidth())
		self.btn_menu4.setSizePolicy(sizePolicy)
		self.btn_menu4.setMinimumSize(QSize(35, 35))
		self.btn_menu4.setMaximumSize(QSize(16777215, 35))
		self.btn_menu4.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

		self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

		self.btn_menu5 = Botao_Personalizado(self.tela_menu, 4)
		self.btn_menu5.setObjectName(u"btn_menu5")
		sizePolicy.setHeightForWidth(self.btn_menu5.sizePolicy().hasHeightForWidth())
		self.btn_menu5.setSizePolicy(sizePolicy)
		self.btn_menu5.setMinimumSize(QSize(35, 35))
		self.btn_menu5.setMaximumSize(QSize(16777215, 35))
		self.btn_menu5.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

		self.line_2 = QFrame(self.tela_menu)
		self.line_2.setObjectName(u"line_2")
		self.line_2.setFrameShadow(QFrame.Plain)
		self.line_2.setFrameShape(QFrame.HLine)

		self.btn_menu6 = Botao_Personalizado(self.tela_menu, 5)
		self.btn_menu6.setObjectName(u"btn_menu6")
		sizePolicy.setHeightForWidth(self.btn_menu6.sizePolicy().hasHeightForWidth())
		self.btn_menu6.setSizePolicy(sizePolicy)
		self.btn_menu6.setMinimumSize(QSize(35, 35))
		self.btn_menu6.setMaximumSize(QSize(16777215, 35))
		self.btn_menu6.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

		self.botoes_menu = []

		self.botoes_menu.append(self.btn_menu1)
		self.botoes_menu.append(self.btn_menu2)
		self.botoes_menu.append(self.btn_menu3)
		self.botoes_menu.append(self.btn_menu4)
		self.botoes_menu.append(self.btn_menu5)
		self.botoes_menu.append(self.btn_menu6)


		self.verticalLayout_15.addWidget(self.btn_menu1)
		self.verticalLayout_15.addWidget(self.btn_menu2)
		self.verticalLayout_15.addWidget(self.btn_menu3)
		self.verticalLayout_15.addWidget(self.btn_menu4)
		self.verticalLayout_15.addItem(self.verticalSpacer)
		self.verticalLayout_15.addWidget(self.btn_menu5)
		self.verticalLayout_15.addWidget(self.line_2)
		self.verticalLayout_15.addWidget(self.btn_menu6)
		self.horizontalLayout.addWidget(self.tela_menu)

		self.paginas = QStackedWidget(self.tela_central)
		self.paginas.setObjectName(u"paginas")
		self.pagina_1 = QWidget()
		self.pagina_1.setObjectName(u"pagina_1")
		self.pagina_1.setMinimumSize(QSize(800, 0))
		self.verticalLayout = QVBoxLayout(self.pagina_1)
		self.verticalLayout.setObjectName(u"verticalLayout")
		self.scroll_1 = QScrollArea(self.pagina_1)
		self.scroll_1.setObjectName(u"scroll_1")
		self.scroll_1.setFrameShape(QFrame.NoFrame)
		self.scroll_1.setWidgetResizable(True)
		self.tela_1 = QWidget()
		self.tela_1.setObjectName(u"tela_1")
		self.tela_1.setGeometry(QRect(0, 0, 837, 561))
		self.gridLayout = QGridLayout(self.tela_1)
		self.gridLayout.setObjectName(u"gridLayout")
		self.tela_c1 = QFrame(self.tela_1)
		self.tela_c1.setObjectName(u"tela_c1")
		self.verticalLayout_3 = QVBoxLayout(self.tela_c1)
		self.verticalLayout_3.setObjectName(u"verticalLayout_3")
		self.frame_2 = QFrame(self.tela_c1)
		self.frame_2.setObjectName(u"frame_2")
		self.horizontalLayout_2 = QHBoxLayout(self.frame_2)
		self.horizontalLayout_2.setSpacing(0)
		self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
		self.input_categorias = Combo_Personalizado(self.frame_2)
		self.input_categorias.addItem("")
		self.input_categorias.addItem("")
		self.input_categorias.addItem("")
		self.input_categorias.addItem("")
		self.input_categorias.addItem("")
		self.input_categorias.addItem("")
		self.input_categorias.addItem("")
		self.input_categorias.addItem("")
		self.input_categorias.addItem("")
		self.input_categorias.addItem("")
		self.input_categorias.addItem("")
		self.input_categorias.setObjectName(u"input_categorias")
		self.input_categorias.setMinimumSize(QSize(150, 30))
		self.input_categorias.setMaximumSize(QSize(150, 30))


		#setattr(self.input_categorias, "allItems", lambda: [self.input_categorias.itemText(i) for i in range(self.input_categorias.count())])

		self.horizontalLayout_2.addWidget(self.input_categorias)

		self.input_pesquisar = QLineEdit(self.frame_2)
		self.input_pesquisar.setObjectName(u"input_pesquisar")
		self.input_pesquisar.setMinimumSize(QSize(300, 30))
		self.input_pesquisar.setMaximumSize(QSize(300, 30))
		self.input_pesquisar.setMaxLength(27)
		self.input_pesquisar.setClearButtonEnabled(True)

		self.horizontalLayout_2.addWidget(self.input_pesquisar)


		self.verticalLayout_3.addWidget(self.frame_2, 0, Qt.AlignHCenter)

		self.line = QFrame(self.tela_c1)
		self.line.setObjectName(u"line")
		self.line.setFrameShadow(QFrame.Plain)
		self.line.setFrameShape(QFrame.HLine)

		self.verticalLayout_3.addWidget(self.line)

		self.horizontalLayout_3 = QHBoxLayout()
		self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
		self.btn_opcoes = QToolButton(self.tela_c1)
		self.btn_opcoes.setObjectName(u"btn_opcoes")
		self.btn_opcoes.setMinimumSize(QSize(30, 30))
		self.btn_opcoes.setMaximumSize(QSize(30, 30))
		self.btn_opcoes.setPopupMode(QToolButton.InstantPopup)
		self.btn_opcoes.setMenu(menu_opcoes)

		self.horizontalLayout_3.addWidget(self.btn_opcoes, 0, Qt.AlignLeft)

		self.rotulo_pesquisas = QLabel(self.tela_c1)
		self.rotulo_pesquisas.setObjectName(u"rotulo_pesquisas")
		self.rotulo_pesquisas.setAlignment(Qt.AlignCenter)
		self.rotulo_pesquisas.setWordWrap(True)
		self.rotulo_pesquisas.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)

		self.horizontalLayout_3.addWidget(self.rotulo_pesquisas)



		self.btn_modo = QToolButton(self.tela_c1)
		self.btn_modo.setObjectName(u"btn_modo")
		self.btn_modo.setMinimumSize(QSize(30, 30))
		self.btn_modo.setMaximumSize(QSize(30, 30))
		self.btn_modo.setPopupMode(QToolButton.InstantPopup)
		self.btn_modo.setMenu(menu_mode)


		self.horizontalLayout_3.addWidget(self.btn_modo, 0, Qt.AlignRight)


		self.verticalLayout_3.addLayout(self.horizontalLayout_3)


		self.gridLayout.addWidget(self.tela_c1, 0, 0, 1, 1, Qt.AlignTop)

		self.tela_vazia = QFrame(self.tela_1)
		self.tela_vazia.setObjectName(u"tela_vazia")
		self.tela_vazia.hide()
		self.horizontalLayout_4 = QHBoxLayout(self.tela_vazia)
		self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
		self.icone_cacto = QPushButton(self.tela_vazia)
		self.icone_cacto.setObjectName(u"icone_cacto")

		self.horizontalLayout_4.addWidget(self.icone_cacto, 0, Qt.AlignHCenter)


		self.gridLayout.addWidget(self.tela_vazia, 1, 0, 1, 1, Qt.AlignTop)

		self.lista_conteudo = QListWidget(self.tela_1)
		self.lista_conteudo.setObjectName(u"lista_conteudo")
		self.lista_conteudo.setFrameShape(QFrame.NoFrame)
		self.lista_conteudo.setFrameShadow(QFrame.Plain)
		self.lista_conteudo.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.lista_conteudo.setProperty("showDropIndicator", False)
		self.lista_conteudo.setSelectionMode(QAbstractItemView.NoSelection)
		self.lista_conteudo.setIconSize(QSize(96, 96))
		self.lista_conteudo.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
		self.lista_conteudo.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
		self.lista_conteudo.setMovement(QListView.Static)
		self.lista_conteudo.setFlow(QListView.LeftToRight)
		self.lista_conteudo.setResizeMode(QListView.Adjust)
		self.lista_conteudo.setSpacing(10)
		self.lista_conteudo.setViewMode(QListView.IconMode)
		self.lista_conteudo.setFocusPolicy(Qt.NoFocus)

		self.lista_conteudo.verticalScrollBar().setSingleStep(20)
		self.lista_conteudo.horizontalScrollBar().setSingleStep(20)

		self.gridLayout.addWidget(self.lista_conteudo, 2, 0, 1, 1)

		self.scroll_1.setWidget(self.tela_1)

		self.verticalLayout.addWidget(self.scroll_1)

		self.paginas.addWidget(self.pagina_1)
		self.pagina_2 = QWidget()
		self.pagina_2.setObjectName(u"pagina_2")
		self.verticalLayout_2 = QVBoxLayout(self.pagina_2)
		self.verticalLayout_2.setObjectName(u"verticalLayout_2")
		self.scroll_2 = QScrollArea(self.pagina_2)
		self.scroll_2.setObjectName(u"scroll_2")
		self.scroll_2.setFrameShape(QFrame.NoFrame)
		self.scroll_2.setWidgetResizable(True)
		self.tela_2 = QWidget()
		self.tela_2.setObjectName(u"tela_2")
		self.tela_2.setGeometry(QRect(0, 0, 336, 484))
		self.gridLayout_2 = QGridLayout(self.tela_2)
		self.gridLayout_2.setObjectName(u"gridLayout_2")
		self.btn_p2 = QPushButton(self.tela_2)
		self.btn_p2.setObjectName(u"btn_p2")
		self.btn_p2.setMinimumSize(QSize(200, 30))
		self.btn_p2.setMaximumSize(QSize(16777215, 30))
		self.btn_p2.setEnabled(False)

		self.gridLayout_2.addWidget(self.btn_p2, 2, 0, 1, 1, Qt.AlignHCenter|Qt.AlignBottom)

		self.tela_cc2 = QFrame(self.tela_2)
		self.tela_cc2.setObjectName(u"tela_cc2")
		self.verticalLayout_4 = QVBoxLayout(self.tela_cc2)
		self.verticalLayout_4.setObjectName(u"verticalLayout_4")
		self.input_imagem = Botao_Drop_Personalizado(self, 330)
		self.input_imagem.setObjectName(u"input_imagem")
		self.input_imagem.setMinimumSize(QSize(300, 300))
		self.input_imagem.setMaximumSize(QSize(300, 300))
		self.input_imagem.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
		self.input_imagem.setToolTip(u"Arraste uma imagem aqui!")

		self.verticalLayout_4.addWidget(self.input_imagem, 0, Qt.AlignHCenter)


		self.gridLayout_2.addWidget(self.tela_cc2, 1, 0, 1, 1)

		self.tela_c2 = QFrame(self.tela_2)
		self.tela_c2.setObjectName(u"tela_c2")
		self.horizontalLayout_5 = QHBoxLayout(self.tela_c2)
		self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
		self.rotulo_c2 = QLabel(self.tela_c2)
		self.rotulo_c2.setObjectName(u"rotulo_c2")
		self.rotulo_c2.setAlignment(Qt.AlignCenter)
		self.rotulo_c2.setWordWrap(True)

		self.horizontalLayout_5.addWidget(self.rotulo_c2)


		self.gridLayout_2.addWidget(self.tela_c2, 0, 0, 1, 1, Qt.AlignTop)

		self.scroll_2.setWidget(self.tela_2)

		self.verticalLayout_2.addWidget(self.scroll_2)

		self.paginas.addWidget(self.pagina_2)
		self.pagina_3 = QWidget()
		self.pagina_3.setObjectName(u"pagina_3")
		self.verticalLayout_5 = QVBoxLayout(self.pagina_3)
		self.verticalLayout_5.setObjectName(u"verticalLayout_5")
		self.scroll_3 = QScrollArea(self.pagina_3)
		self.scroll_3.setObjectName(u"scroll_3")
		self.scroll_3.setFrameShape(QFrame.NoFrame)
		self.scroll_3.setWidgetResizable(True)
		self.tela_3 = QWidget()
		self.tela_3.setObjectName(u"tela_3")
		self.tela_3.setGeometry(QRect(0, 0, 710, 472))
		self.verticalLayout_6 = QVBoxLayout(self.tela_3)
		self.verticalLayout_6.setObjectName(u"verticalLayout_6")
		self.tela_c3 = QFrame(self.tela_3)
		self.tela_c3.setObjectName(u"tela_c3")
		self.horizontalLayout_6 = QHBoxLayout(self.tela_c3)
		self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
		self.btn_voltar_c3 = QToolButton(self.tela_c3)
		self.btn_voltar_c3.setObjectName(u"btn_voltar_c3")
		self.btn_voltar_c3.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

		self.horizontalLayout_6.addWidget(self.btn_voltar_c3, 0, Qt.AlignTop)

		self.rotulo_c3 = QLabel(self.tela_c3)
		self.rotulo_c3.setObjectName(u"rotulo_c3")
		self.rotulo_c3.setAlignment(Qt.AlignCenter)
		self.rotulo_c3.setWordWrap(True)

		self.horizontalLayout_6.addWidget(self.rotulo_c3, 0, Qt.AlignTop)

		self.label_2 = QLabel(self.tela_c3)
		self.label_2.setObjectName(u"label_2")
		self.label_2.setEnabled(False)
		self.label_2.setMaximumSize(QSize(1, 1))
		self.label_2.setTextInteractionFlags(Qt.NoTextInteraction)

		self.horizontalLayout_6.addWidget(self.label_2)


		self.verticalLayout_6.addWidget(self.tela_c3, 0, Qt.AlignTop)

		self.tela_cc3 = QGroupBox(self.tela_3)
		self.tela_cc3.setObjectName(u"tela_cc3")
		self.tela_cc3.setMaximumSize(QSize(700, 16777215))
		self.horizontalLayout_14 = QHBoxLayout(self.tela_cc3)
		self.horizontalLayout_14.setSpacing(30)
		self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
		self.horizontalLayout_14.setContentsMargins(15, 15, 15, 15)
		self.input_filtro_1 = QToolButton(self.tela_cc3)
		self.input_filtro_1.setObjectName(u"input_filtro_1")
		self.input_filtro_1.setMinimumSize(QSize(200, 250))
		self.input_filtro_1.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

		self.horizontalLayout_14.addWidget(self.input_filtro_1)


		self.input_filtro_2 = QToolButton(self.tela_cc3)
		self.input_filtro_2.setObjectName(u"input_filtro_2")
		self.input_filtro_2.setMinimumSize(QSize(200, 250))
		self.input_filtro_2.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

		self.horizontalLayout_14.addWidget(self.input_filtro_2)

		self.input_filtro_3 = QToolButton(self.tela_cc3)
		self.input_filtro_3.setObjectName(u"input_filtro_3")
		self.input_filtro_3.setMinimumSize(QSize(200, 250))
		self.input_filtro_3.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

		self.horizontalLayout_14.addWidget(self.input_filtro_3)

		self.verticalLayout_6.addWidget(self.tela_cc3, 0, Qt.AlignHCenter)

		self.tela_ccc3 = QFrame(self.tela_3)
		self.tela_ccc3.setObjectName(u"tela_ccc3")
		self.tela_ccc3.setFrameShape(QFrame.StyledPanel)
		self.tela_ccc3.setFrameShadow(QFrame.Raised)
		self.horizontalLayout_7 = QHBoxLayout(self.tela_ccc3)
		self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
		self.label = QLabel(self.tela_ccc3)
		self.label.setObjectName(u"label")
		self.label.setAlignment(Qt.AlignCenter)
		self.label.setWordWrap(True)

		self.horizontalLayout_7.addWidget(self.label)


		self.verticalLayout_6.addWidget(self.tela_ccc3, 0, Qt.AlignBottom)

		self.scroll_3.setWidget(self.tela_3)

		self.verticalLayout_5.addWidget(self.scroll_3)

		self.paginas.addWidget(self.pagina_3)
		self.pagina_4 = QWidget()
		self.pagina_4.setObjectName(u"pagina_4")
		self.verticalLayout_7 = QVBoxLayout(self.pagina_4)
		self.verticalLayout_7.setObjectName(u"verticalLayout_7")
		self.scroll_4 = QScrollArea(self.pagina_4)
		self.scroll_4.setObjectName(u"scroll_4")
		self.scroll_4.setFrameShape(QFrame.NoFrame)
		self.scroll_4.setWidgetResizable(True)
		self.tela_4 = QWidget()
		self.tela_4.setObjectName(u"tela_4")
		self.tela_4.setGeometry(QRect(0, 0, 816, 443))
		self.verticalLayout_8 = QVBoxLayout(self.tela_4)
		self.verticalLayout_8.setObjectName(u"verticalLayout_8")
		self.tela_c4 = QFrame(self.tela_4)
		self.tela_c4.setObjectName(u"tela_c4")
		self.horizontalLayout_9 = QHBoxLayout(self.tela_c4)
		self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
		self.btn_voltar_c4 = QToolButton(self.tela_c4)
		self.btn_voltar_c4.setObjectName(u"btn_voltar_c4")
		self.btn_voltar_c4.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

		self.horizontalLayout_9.addWidget(self.btn_voltar_c4, 0, Qt.AlignTop)

		self.rotulo_c4 = QLabel(self.tela_c4)
		self.rotulo_c4.setObjectName(u"rotulo_c4")
		self.rotulo_c4.setAlignment(Qt.AlignCenter)
		self.rotulo_c4.setWordWrap(True)

		self.horizontalLayout_9.addWidget(self.rotulo_c4, 0, Qt.AlignTop)

		self.btn_editor = QToolButton(self.tela_c4)
		self.btn_editor.setObjectName(u"btn_editor")
		self.btn_editor.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

		self.horizontalLayout_9.addWidget(self.btn_editor, 0, Qt.AlignTop)


		self.verticalLayout_8.addWidget(self.tela_c4, 0, Qt.AlignTop)

		self.tela_cc4 = QFrame(self.tela_4)
		self.tela_cc4.setObjectName(u"tela_cc4")
		self.gridLayout_3 = QGridLayout(self.tela_cc4)
		self.gridLayout_3.setSpacing(20)
		self.gridLayout_3.setObjectName(u"gridLayout_3")
		self.rotulo_filtro = QPushButton(self.tela_cc4)
		self.rotulo_filtro.setObjectName(u"rotulo_filtro")

		self.gridLayout_3.addWidget(self.rotulo_filtro, 0, 0, 1, 1, Qt.AlignLeft)

		self.img_bmp = QLabel(self.tela_cc4)
		self.img_bmp.setObjectName(u"img_bmp")
		self.img_bmp.setMinimumSize(QSize(220, 220))
		self.img_bmp.setMaximumSize(QSize(220, 220))
		self.img_bmp.setAlignment(Qt.AlignCenter)

		self.gridLayout_3.addWidget(self.img_bmp, 1, 0, 1, 1)

		self.icone_seta_dupla = QPushButton(self.tela_cc4)
		self.icone_seta_dupla.setObjectName(u"icone_seta_dupla")

		self.gridLayout_3.addWidget(self.icone_seta_dupla, 1, 1, 1, 1)

		self.img_svg = QLabel(self.tela_cc4)
		self.img_svg.setObjectName(u"img_svg")
		self.img_svg.setMinimumSize(QSize(220, 220))
		self.img_svg.setMaximumSize(QSize(220, 220))
		self.img_svg.setAlignment(Qt.AlignCenter)

		self.gridLayout_3.addWidget(self.img_svg, 1, 2, 1, 1)

		self.icone_seta_dupla_2 = QPushButton(self.tela_cc4)
		self.icone_seta_dupla_2.setObjectName(u"icone_seta_dupla_2")

		self.gridLayout_3.addWidget(self.icone_seta_dupla_2, 1, 3, 1, 1)

		self.img_final = QLabel(self.tela_cc4)
		self.img_final.setObjectName(u"img_final")
		self.img_final.setMinimumSize(QSize(220, 220))
		self.img_final.setMaximumSize(QSize(220, 220))
		self.img_final.setAlignment(Qt.AlignCenter)

		self.gridLayout_3.addWidget(self.img_final, 1, 4, 1, 1)

		self.label_7 = QLabel(self.tela_cc4)
		self.label_7.setObjectName(u"label_7")
		self.label_7.setMaximumSize(QSize(16777215, 20))
		self.label_7.setAlignment(Qt.AlignCenter)

		self.gridLayout_3.addWidget(self.label_7, 2, 0, 1, 1)

		self.label_8 = QLabel(self.tela_cc4)
		self.label_8.setObjectName(u"label_8")
		self.label_8.setAlignment(Qt.AlignCenter)

		self.gridLayout_3.addWidget(self.label_8, 2, 2, 1, 1)

		self.label_9 = QLabel(self.tela_cc4)
		self.label_9.setObjectName(u"label_9")
		self.label_9.setAlignment(Qt.AlignCenter)

		self.gridLayout_3.addWidget(self.label_9, 2, 4, 1, 1)


		self.verticalLayout_8.addWidget(self.tela_cc4, 0, Qt.AlignHCenter)

		self.btn_p4 = QPushButton(self.tela_4)
		self.btn_p4.setObjectName(u"btn_p4")
		self.btn_p4.setMinimumSize(QSize(200, 30))
		self.btn_p4.setMaximumSize(QSize(16777215, 30))

		self.verticalLayout_8.addWidget(self.btn_p4, 0, Qt.AlignHCenter|Qt.AlignBottom)

		self.scroll_4.setWidget(self.tela_4)

		self.verticalLayout_7.addWidget(self.scroll_4)

		self.paginas.addWidget(self.pagina_4)
		self.pagina_5 = QWidget()
		self.pagina_5.setObjectName(u"pagina_5")
		self.verticalLayout_9 = QVBoxLayout(self.pagina_5)
		self.verticalLayout_9.setObjectName(u"verticalLayout_9")
		self.scroll_5 = QScrollArea(self.pagina_5)
		self.scroll_5.setObjectName(u"scroll_5")
		self.scroll_5.setFrameShape(QFrame.NoFrame)
		self.scroll_5.setWidgetResizable(True)
		self.scroll_5.setAlignment(Qt.AlignCenter)
		self.tela_5 = QWidget()
		self.tela_5.setObjectName(u"tela_5")
		self.tela_5.setGeometry(QRect(0, 0, 521, 541))
		self.gridLayout_5 = QGridLayout(self.tela_5)
		self.gridLayout_5.setObjectName(u"gridLayout_5")
		self.tela_cc5 = QFrame(self.tela_5)
		self.tela_cc5.setObjectName(u"tela_cc5")
		self.horizontalLayout_12 = QHBoxLayout(self.tela_cc5)
		self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
		self.tela_config_desenho = QGroupBox(self.tela_cc5)
		self.tela_config_desenho.setObjectName(u"tela_config_desenho")
		self.tela_config_desenho.setMinimumSize(QSize(0, 0))
		self.tela_config_desenho.setMaximumSize(QSize(700, 16777215))
		self.verticalLayout_10 = QVBoxLayout(self.tela_config_desenho)
		self.verticalLayout_10.setSpacing(10)
		self.verticalLayout_10.setObjectName(u"verticalLayout_10")
		self.verticalLayout_10.setContentsMargins(20, 15, 20, 15)
		self.gridLayout_9 = QGridLayout()
		self.gridLayout_9.setObjectName(u"gridLayout_9")
		self.icone_monitor = QPushButton(self.tela_config_desenho)
		self.icone_monitor.setObjectName(u"icone_monitor")

		self.gridLayout_9.addWidget(self.icone_monitor, 0, 0, 1, 1)

		self.icone_tamanho_img = QPushButton(self.tela_config_desenho)
		self.icone_tamanho_img.setObjectName(u"icone_tamanho_img")

		self.gridLayout_9.addWidget(self.icone_tamanho_img, 0, 1, 1, 1)

		self.line_3 = QFrame(self.tela_config_desenho)
		self.line_3.setObjectName(u"line_3")
		self.line_3.setFrameShadow(QFrame.Plain)
		self.line_3.setFrameShape(QFrame.HLine)

		self.gridLayout_9.addWidget(self.line_3, 1, 0, 1, 2)


		self.verticalLayout_10.addLayout(self.gridLayout_9)

		self.gridLayout_8 = QGridLayout()
		self.gridLayout_8.setObjectName(u"gridLayout_8")
		self.icone_altura = QPushButton(self.tela_config_desenho)
		self.icone_altura.setObjectName(u"icone_altura")

		self.gridLayout_8.addWidget(self.icone_altura, 1, 0, 1, 1, Qt.AlignLeft)

		self.input_altura = QSpinBox(self.tela_config_desenho)
		self.input_altura.setObjectName(u"input_altura")
		self.input_altura.setMinimumSize(QSize(0, 30))
		self.input_altura.setMaximumSize(QSize(350, 30))
		self.input_altura.setMinimum(20)
		self.input_altura.setMaximum(4000)
		self.input_altura.setSingleStep(1)
		self.input_altura.setValue(20)

		self.gridLayout_8.addWidget(self.input_altura, 2, 0, 1, 1)

		self.input_proporcao = QToolButton(self.tela_config_desenho)
		self.input_proporcao.setObjectName(u"input_proporcao")
		self.input_proporcao.setMinimumSize(QSize(30, 30))
		self.input_proporcao.setMaximumSize(QSize(30, 30))
		self.input_proporcao.setCheckable(True)
		self.input_proporcao.setChecked(True)

		self.gridLayout_8.addWidget(self.input_proporcao, 2, 1, 1, 1)

		self.input_largura = QSpinBox(self.tela_config_desenho)
		self.input_largura.setObjectName(u"input_largura")
		self.input_largura.setMinimumSize(QSize(0, 30))
		self.input_largura.setMaximumSize(QSize(350, 30))
		self.input_largura.setMinimum(20)
		self.input_largura.setMaximum(4000)
		self.input_largura.setSingleStep(1)
		self.input_largura.setValue(20)

		self.gridLayout_8.addWidget(self.input_largura, 2, 2, 1, 1)

		self.icone_largura = QPushButton(self.tela_config_desenho)
		self.icone_largura.setObjectName(u"icone_largura")

		self.gridLayout_8.addWidget(self.icone_largura, 1, 2, 1, 1, Qt.AlignLeft)

		self.label_5 = QLabel(self.tela_config_desenho)
		self.label_5.setObjectName(u"label_5")
		self.label_5.setMaximumSize(QSize(16777215, 20))

		self.gridLayout_8.addWidget(self.label_5, 0, 0, 1, 3)


		self.verticalLayout_10.addLayout(self.gridLayout_8)

		self.icone_velocidade = QPushButton(self.tela_config_desenho)
		self.icone_velocidade.setObjectName(u"icone_velocidade")

		self.verticalLayout_10.addWidget(self.icone_velocidade, 0, Qt.AlignLeft)

		self.horizontalLayout_11 = QHBoxLayout()
		self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
		self.input_lento = QRadioButton(self.tela_config_desenho)
		self.input_lento.setObjectName(u"input_lento")

		self.horizontalLayout_11.addWidget(self.input_lento)

		self.input_normal = QRadioButton(self.tela_config_desenho)
		self.input_normal.setObjectName(u"input_normal")
		self.input_normal.setChecked(True)

		self.horizontalLayout_11.addWidget(self.input_normal)

		self.input_rapido = QRadioButton(self.tela_config_desenho)
		self.input_rapido.setObjectName(u"input_rapido")

		self.horizontalLayout_11.addWidget(self.input_rapido)

		self.input_mt_rapido = QRadioButton(self.tela_config_desenho)
		self.input_mt_rapido.setObjectName(u"input_mt_rapido")

		self.horizontalLayout_11.addWidget(self.input_mt_rapido)

		self.input_manual = QRadioButton(self.tela_config_desenho)
		self.input_manual.setObjectName(u"input_manual")

		self.horizontalLayout_11.addWidget(self.input_manual)


		self.verticalLayout_10.addLayout(self.horizontalLayout_11)

		self.label_10 = QLabel(self.tela_config_desenho)
		self.label_10.setObjectName(u"label_10")

		self.verticalLayout_10.addWidget(self.label_10)

		self.input_densidade = QSpinBox(self.tela_config_desenho)
		self.input_densidade.setObjectName(u"input_densidade")
		self.input_densidade.setEnabled(False)
		self.input_densidade.setMinimumSize(QSize(0, 30))
		self.input_densidade.setMaximumSize(QSize(16777215, 30))
		self.input_densidade.setAccelerated(True)
		self.input_densidade.setMinimum(50)
		self.input_densidade.setMaximum(65000)
		self.input_densidade.setSingleStep(50)
		self.input_densidade.setValue(7000)

		self.verticalLayout_10.addWidget(self.input_densidade)

		self.gridLayout_4 = QGridLayout()
		self.gridLayout_4.setObjectName(u"gridLayout_4")
		self.input_nome_desenho = QLineEdit(self.tela_config_desenho)
		self.input_nome_desenho.setObjectName(u"input_nome_desenho")
		self.input_nome_desenho.setMinimumSize(QSize(0, 30))
		self.input_nome_desenho.setMaximumSize(QSize(350, 30))
		self.input_nome_desenho.setMaxLength(27)
		self.input_nome_desenho.setClearButtonEnabled(True)

		self.gridLayout_4.addWidget(self.input_nome_desenho, 1, 2, 1, 1)

		self.input_categoria = Combo_Personalizado(self.tela_config_desenho)
		self.input_categoria.addItem("")
		self.input_categoria.addItem("")
		self.input_categoria.addItem("")
		self.input_categoria.addItem("")
		self.input_categoria.addItem("")
		self.input_categoria.addItem("")
		self.input_categoria.addItem("")
		self.input_categoria.addItem("")
		self.input_categoria.addItem("")
		self.input_categoria.addItem("")
		self.input_categoria.addItem("")
		self.input_categoria.setObjectName(u"input_categoria")
		self.input_categoria.setMinimumSize(QSize(0, 30))
		self.input_categoria.setMaximumSize(QSize(350, 30))
		self.input_categoria.setEditable(False)

		self.gridLayout_4.addWidget(self.input_categoria, 1, 0, 1, 2)

		self.icone_nome_desenho = QPushButton(self.tela_config_desenho)
		self.icone_nome_desenho.setObjectName(u"icone_nome_desenho")

		self.gridLayout_4.addWidget(self.icone_nome_desenho, 0, 2, 1, 1, Qt.AlignLeft)

		self.icone_categoria = QPushButton(self.tela_config_desenho)
		self.icone_categoria.setObjectName(u"icone_categoria")

		self.gridLayout_4.addWidget(self.icone_categoria, 0, 0, 1, 2, Qt.AlignLeft)


		self.verticalLayout_10.addLayout(self.gridLayout_4)

		self.horizontalLayout_12.addWidget(self.tela_config_desenho)


		self.gridLayout_5.addWidget(self.tela_cc5, 1, 0, 1, 1)

		self.btn_p5 = QPushButton(self.tela_5)
		self.btn_p5.setObjectName(u"btn_p5")
		self.btn_p5.setMinimumSize(QSize(200, 30))
		self.btn_p5.setMaximumSize(QSize(16777215, 30))

		self.gridLayout_5.addWidget(self.btn_p5, 2, 0, 1, 1, Qt.AlignHCenter|Qt.AlignBottom)

		self.tela_c5 = QFrame(self.tela_5)
		self.tela_c5.setObjectName(u"tela_c5")
		self.horizontalLayout_10 = QHBoxLayout(self.tela_c5)
		self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
		self.btn_voltar_c5 = QToolButton(self.tela_c5)
		self.btn_voltar_c5.setObjectName(u"btn_voltar_c5")
		self.btn_voltar_c5.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

		self.horizontalLayout_10.addWidget(self.btn_voltar_c5, 0, Qt.AlignTop)

		self.rotulo_c5 = QLabel(self.tela_c5)
		self.rotulo_c5.setObjectName(u"rotulo_c5")
		self.rotulo_c5.setAlignment(Qt.AlignCenter)
		self.rotulo_c5.setWordWrap(True)

		self.horizontalLayout_10.addWidget(self.rotulo_c5, 0, Qt.AlignTop)

		self.btn_ajuda_c5 = QToolButton(self.tela_c5)
		self.btn_ajuda_c5.setObjectName(u"btn_ajuda_c5")
		self.btn_ajuda_c5.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

		self.horizontalLayout_10.addWidget(self.btn_ajuda_c5, 0, Qt.AlignTop)


		self.gridLayout_5.addWidget(self.tela_c5, 0, 0, 1, 1, Qt.AlignTop)

		self.scroll_5.setWidget(self.tela_5)

		self.verticalLayout_9.addWidget(self.scroll_5)

		self.paginas.addWidget(self.pagina_5)
		self.pagina_6 = QWidget()
		self.pagina_6.setObjectName(u"pagina_6")
		self.verticalLayout_11 = QVBoxLayout(self.pagina_6)
		self.verticalLayout_11.setObjectName(u"verticalLayout_11")
		self.scroll_6 = QScrollArea(self.pagina_6)
		self.scroll_6.setObjectName(u"scroll_6")
		self.scroll_6.setFrameShape(QFrame.NoFrame)
		self.scroll_6.setWidgetResizable(True)
		self.tela_6 = QWidget()
		self.tela_6.setObjectName(u"tela_6")
		self.tela_6.setGeometry(QRect(0, 0, 556, 541))
		self.verticalLayout_13 = QVBoxLayout(self.tela_6)
		self.verticalLayout_13.setObjectName(u"verticalLayout_13")
		self.tela_c6 = QFrame(self.tela_6)
		self.tela_c6.setObjectName(u"tela_c6")
		self.verticalLayout_14 = QVBoxLayout(self.tela_c6)
		self.verticalLayout_14.setObjectName(u"verticalLayout_14")
		self.gif_carregamento = QLabel(self.tela_c6)
		self.gif_carregamento.setObjectName(u"gif_carregamento")
		self.gif_carregamento.setMinimumSize(QSize(150, 150))
		self.gif_carregamento.setMaximumSize(QSize(150, 150))
		self.gif_carregamento.setAlignment(Qt.AlignCenter)

		self.verticalLayout_14.addWidget(self.gif_carregamento, 0, Qt.AlignHCenter)

		self.rotulo_c6 = QLabel(self.tela_c6)
		self.rotulo_c6.setObjectName(u"rotulo_c6")
		self.rotulo_c6.setAlignment(Qt.AlignCenter)

		self.verticalLayout_14.addWidget(self.rotulo_c6)


		self.verticalLayout_13.addWidget(self.tela_c6, 0, Qt.AlignTop)

		self.tela_cc6 = QFrame(self.tela_6)
		self.tela_cc6.setObjectName(u"tela_cc6")
		self.horizontalLayout_13 = QHBoxLayout(self.tela_cc6)
		self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
		self.tela_resultado = QGroupBox(self.tela_cc6)
		self.tela_resultado.setObjectName(u"tela_resultado")
		self.tela_resultado.setMaximumSize(QSize(700, 16777215))
		self.verticalLayout_12 = QVBoxLayout(self.tela_resultado)
		self.verticalLayout_12.setObjectName(u"verticalLayout_12")
		self.icone_concluido = QPushButton(self.tela_resultado)
		self.icone_concluido.setObjectName(u"icone_concluido")

		self.verticalLayout_12.addWidget(self.icone_concluido, 0, Qt.AlignHCenter)

		self.rotulo_r = QLabel(self.tela_resultado)
		self.rotulo_r.setObjectName(u"rotulo_r")
		self.rotulo_r.setAlignment(Qt.AlignCenter)

		self.verticalLayout_12.addWidget(self.rotulo_r)

		self.frame_24 = QFrame(self.tela_resultado)
		self.frame_24.setObjectName(u"frame_24")
		self.frame_24.setMinimumSize(QSize(500, 0))
		self.gridLayout_11 = QGridLayout(self.frame_24)
		self.gridLayout_11.setObjectName(u"gridLayout_11")
		self.icone3_cc6 = QToolButton(self.frame_24)
		self.icone3_cc6.setObjectName(u"icone3_cc6")
		self.icone3_cc6.setFocusPolicy(Qt.NoFocus)
		self.icone3_cc6.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

		self.gridLayout_11.addWidget(self.icone3_cc6, 4, 0, 1, 1)

		self.icone5_cc6 = QToolButton(self.frame_24)
		self.icone5_cc6.setObjectName(u"icone5_cc6")
		self.icone5_cc6.setFocusPolicy(Qt.NoFocus)
		self.icone5_cc6.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

		self.gridLayout_11.addWidget(self.icone5_cc6, 0, 2, 1, 1)

		self.icone4_cc6 = QToolButton(self.frame_24)
		self.icone4_cc6.setObjectName(u"icone4_cc6")
		self.icone4_cc6.setFocusPolicy(Qt.NoFocus)
		self.icone4_cc6.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

		self.gridLayout_11.addWidget(self.icone4_cc6, 4, 2, 1, 1)

		self.icone6_cc6 = QToolButton(self.frame_24)
		self.icone6_cc6.setObjectName(u"icone6_cc6")
		self.icone6_cc6.setFocusPolicy(Qt.NoFocus)
		self.icone6_cc6.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

		self.gridLayout_11.addWidget(self.icone6_cc6, 2, 2, 1, 1)

		self.icone1_cc6 = QToolButton(self.frame_24)
		self.icone1_cc6.setObjectName(u"icone1_cc6")
		self.icone1_cc6.setFocusPolicy(Qt.NoFocus)
		self.icone1_cc6.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

		self.gridLayout_11.addWidget(self.icone1_cc6, 0, 0, 1, 2)

		self.line_11 = QFrame(self.frame_24)
		self.line_11.setObjectName(u"line_11")
		self.line_11.setFrameShadow(QFrame.Plain)
		self.line_11.setFrameShape(QFrame.HLine)

		self.gridLayout_11.addWidget(self.line_11, 5, 0, 2, 3)

		self.line_10 = QFrame(self.frame_24)
		self.line_10.setObjectName(u"line_10")
		self.line_10.setFrameShadow(QFrame.Plain)
		self.line_10.setFrameShape(QFrame.HLine)

		self.gridLayout_11.addWidget(self.line_10, 3, 0, 1, 3)

		self.icone2_cc6 = QToolButton(self.frame_24)
		self.icone2_cc6.setObjectName(u"icone2_cc6")
		self.icone2_cc6.setFocusPolicy(Qt.NoFocus)
		self.icone2_cc6.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

		self.gridLayout_11.addWidget(self.icone2_cc6, 2, 0, 1, 1)

		self.line_9 = QFrame(self.frame_24)
		self.line_9.setObjectName(u"line_9")
		self.line_9.setFrameShadow(QFrame.Plain)
		self.line_9.setFrameShape(QFrame.HLine)

		self.gridLayout_11.addWidget(self.line_9, 1, 0, 1, 3)

		self.icone7_cc6 = QToolButton(self.frame_24)
		self.icone7_cc6.setObjectName(u"icone7_cc6")
		sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
		sizePolicy1.setHorizontalStretch(0)
		sizePolicy1.setVerticalStretch(0)
		sizePolicy1.setHeightForWidth(self.icone7_cc6.sizePolicy().hasHeightForWidth())
		self.icone7_cc6.setSizePolicy(sizePolicy1)
		self.icone7_cc6.setFocusPolicy(Qt.NoFocus)
		self.icone7_cc6.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

		self.gridLayout_11.addWidget(self.icone7_cc6, 7, 0, 1, 3, Qt.AlignHCenter)


		self.verticalLayout_12.addWidget(self.frame_24, 0, Qt.AlignHCenter)


		self.horizontalLayout_13.addWidget(self.tela_resultado)


		self.verticalLayout_13.addWidget(self.tela_cc6, 0, Qt.AlignTop)

		self.btn_p6 = QPushButton(self.tela_6)
		self.btn_p6.setObjectName(u"btn_p6")
		self.btn_p6.setMinimumSize(QSize(200, 30))
		self.btn_p6.setMaximumSize(QSize(16777215, 30))

		self.verticalLayout_13.addWidget(self.btn_p6, 0, Qt.AlignHCenter|Qt.AlignBottom)

		self.scroll_6.setWidget(self.tela_6)

		self.verticalLayout_11.addWidget(self.scroll_6)

		self.paginas.addWidget(self.pagina_6)
		self.pagina_7 = QWidget()
		self.pagina_7.setObjectName(u"pagina_7")
		self.paginas.addWidget(self.pagina_7)

		self.horizontalLayout.addWidget(self.paginas)

		self.setCentralWidget(self.tela_central)
		self.barra_estado = QStatusBar(self)
		self.barra_estado.setObjectName(u"barra_estado")
		self.setStatusBar(self.barra_estado)

		self.retranslateUi()

		self.paginas.setCurrentIndex(0)
		self.btn_p2.setDefault(True)
		self.btn_p4.setDefault(True)
		self.input_categorias.setCurrentIndex(0)
		self.input_categoria.setCurrentIndex(0)
		self.btn_p5.setDefault(True)
		self.btn_p6.setDefault(True)

		# CONEXOES PAGINAS, CONEXOES VOLTAR
		self.btn_menu1.pressed.connect(lambda: self.paginas.setCurrentIndex(0))
		self.btn_menu2.pressed.connect(lambda: self.paginas.setCurrentIndex(1))
		self.btn_menu6.clicked.connect(self.close)
		self.btn_voltar_c3.pressed.connect(lambda: self.paginas.setCurrentIndex(1))
		self.btn_voltar_c4.pressed.connect(lambda: self.paginas.setCurrentIndex(2))
		self.btn_voltar_c5.pressed.connect(lambda: self.paginas.setCurrentIndex(3))
		self.btn_p2.clicked.connect(lambda: self.paginas.setCurrentIndex(2))
		self.btn_editor.clicked.connect(lambda: CamelEditor(self))

		self.input_filtro_1.clicked.connect(lambda: self.ac_temporario_1(filtro = 1))
		self.input_filtro_2.clicked.connect(lambda: self.ac_temporario_1(filtro = 2))
		self.input_filtro_3.clicked.connect(lambda: self.ac_temporario_1(filtro = 3))
		self.btn_menu4.clicked.connect(self.ac_sobre)
		self.btn_menu5.clicked.connect(lambda: CamelConfig(self))


		# CONEXOES OUTRAS AC
		self.input_altura.valueChanged.connect(self.ac_proporcao_altura)
		self.input_largura.valueChanged.connect(self.ac_proporcao_largura)
		self.input_manual.toggled.connect(self.input_densidade.setEnabled)
		self.btn_p4.clicked.connect(self.ac_pagina_resetar)
		self.btn_p5.clicked.connect(self.ac_verificar)
		self.btn_p6.clicked.connect(self.ac_carregar_novo)
		self.btn_menu3.clicked.connect(self.ac_liberar_memoria)
		self.paginas.currentChanged.connect(self.ac_alterar_pagina)
		self.input_pesquisar.textChanged.connect(self.ac_pesquisar)
		self.input_categorias.currentIndexChanged.connect(lambda: self.ac_pesquisar(self.input_pesquisar.text()))

		self.actionMode_Grade.triggered.connect(self.ac_mode_grade)
		self.actionMode_Lista.triggered.connect(self.ac_mode_fileira)
		self.actionRemove_Imagem.triggered.connect(self.ac_esconder_imagem)
		self.actionCor_Fundo.triggered.connect(self.ac_cor_fundo)
		self.btn_ajuda_c5.clicked.connect(self.ac_ajuda)


		QMetaObject.connectSlotsByName(self)

	def retranslateUi(self):

		self.btn_menu1.setText(self.tr(u"	 Meus Desenhos"))
		self.btn_menu2.setText(self.tr(u"	 Criar Novo Desenho"))
		self.btn_menu3.setText(self.tr(u"	 Liberar Memória"))
		self.btn_menu4.setText(self.tr(u"	 Sobre"))
		self.btn_menu5.setText(self.tr(u"	 Configurações"))
		self.btn_menu6.setText(self.tr(u"	 Sair"))
		self.input_pesquisar.setPlaceholderText(self.tr(u"Pesquisar desenhos"))
#if QT_CONFIG(tooltip)
		self.btn_opcoes.setToolTip(self.tr(u"Opções"))
		self.btn_modo.setToolTip(self.tr(u"Visualizar"))
#endif // QT_CONFIG(tooltip)
		self.rotulo_pesquisas.setText(self.tr(u"Meus Desenhos - 0"))
		self.btn_p2.setText(self.tr(u"Próximo"))
		self.input_imagem.setText(self.tr(u"arraste e solte seu documento de imagem\n"
"compatível: jpge, png, gif, tiff...\n"
"\n"
" ou\n"
"\n"
" procure pela imagem"))
		self.rotulo_c2.setText(self.tr(u"<html><head/><body><p><span style=\" font-size:12pt; font-weight:700;\">Adicione uma imagem desejada para seu desenho, você pode adicionar clicando ou arrastando a imagem sobre o quadrado abaixo.</span></p></body></html>"))
		self.btn_voltar_c3.setText(self.tr(u"Voltar"))
		self.rotulo_c3.setText(self.tr(u"<html><head/><body><p><span style=\" font-size:12pt; font-weight:700;\">Adicionar algum filtro para o bitmap poderá obter mais detalhes ao conveter para SVG, depedendo da imagem</span></p></body></html>"))
		self.tela_cc3.setTitle(self.tr(u"Filtros"))
		self.input_filtro_1.setText(self.tr(u"SEM FILTRO"))
		self.input_filtro_3.setText(self.tr(u"REALÇADOS"))
		self.input_filtro_2.setText(self.tr(u"DETALHES"))
		self.label.setText(self.tr(u"Veja um exemplo de uma maça convetida para bitmap depois SVG. Cada filtro pode tornar o desenho final bem mais visivel com o original, dependendo da imagem o processo será bem mais demorado \nDica: Depedendo da quantidade de cores da imagem, levará mais tempo para processar em \"Filtro Realçado\" "))
		self.btn_voltar_c4.setText(self.tr(u"Voltar"))
		self.rotulo_c4.setText(self.tr(u"<html><head/><body><p><span style=\" font-size:12pt; font-weight:700;\">Pré-Visualização do desenho final Você pode editar o desenho final, clicando no botão direito (Editar Desenho)</span></p></body></html>"))
		self.btn_editor.setText(self.tr(u"Editar Desenho"))
		self.rotulo_filtro.setText(self.tr(u"Filtro: "))
		self.label_7.setText(self.tr(u"<html><head/><body><p><span style=\" font-size:10pt; font-weight:700;\">(1) - Convertido Bitmap</span></p></body></html>"))
		self.label_8.setText(self.tr(u"<html><head/><body><p><span style=\" font-size:10pt; font-weight:700;\">(2) - Convertido SVG</span></p></body></html>"))
		self.label_9.setText(self.tr(u"<html><head/><body><p><span style=\" font-size:10pt; font-weight:700;\">(3) - Desenho Final</span></p></body></html>"))
		self.btn_p4.setText(self.tr(u"Próximo"))
		self.tela_config_desenho.setTitle(self.tr(u"Configurações do Desenho"))
		self.icone_monitor.setText(self.tr(u"Tamanho da Tela: Não obtido"))
		self.icone_tamanho_img.setText(self.tr(u"Tamanho da Imagem: Não obtido"))
		self.icone_altura.setText(self.tr(u"Altura (pixel)"))
#if QT_CONFIG(tooltip)
		self.input_proporcao.setToolTip(self.tr(u"Manter taxa de proporção"))
#endif // QT_CONFIG(tooltip)
		self.input_proporcao.setText("")
		self.icone_largura.setText(self.tr(u"Largura (pixel)"))
		self.label_5.setText(self.tr(u"Tamanho largura e altura do desenho."))
		self.icone_velocidade.setText(self.tr(u"Velocidade do desenho, por densidade"))
		self.input_lento.setText(self.tr(u"Lento -30%"))
		self.input_normal.setText(self.tr(u"Normal 0%"))
		self.input_rapido.setText(self.tr(u"Rapido 40%"))
		self.input_mt_rapido.setText(self.tr(u"Rapido 70%"))
		self.input_manual.setText(self.tr(u"Manualmente"))
		self.label_10.setText(self.tr(u"Velocidade manual por densidade Limitado (65000)"))
		self.input_nome_desenho.setPlaceholderText(self.tr(u"Exemplo: Camelo Perdido"))

		self.input_categorias.setItemText(0, self.tr(u"Geral"))
		self.input_categorias.setItemText(1, self.tr(u"Animes"))
		self.input_categorias.setItemText(2, self.tr(u"Alimentos"))
		self.input_categorias.setItemText(3, self.tr(u"Animais"))
		self.input_categorias.setItemText(4, self.tr(u"Desenhos Animados"))
		self.input_categorias.setItemText(5, self.tr(u"Filmes"))
		self.input_categorias.setItemText(6, self.tr(u"Frases"))
		self.input_categorias.setItemText(7, self.tr(u"Favoritos"))
		self.input_categorias.setItemText(8, self.tr(u"Objetos"))
		self.input_categorias.setItemText(9, self.tr(u"Textos"))
		self.input_categorias.setItemText(10, self.tr(u"Personagens"))

		self.input_categoria.setItemText(0, self.tr(u"Geral"))
		self.input_categoria.setItemText(1, self.tr(u"Animes"))
		self.input_categoria.setItemText(2, self.tr(u"Alimentos"))
		self.input_categoria.setItemText(3, self.tr(u"Animais"))
		self.input_categoria.setItemText(4, self.tr(u"Desenhos Animados"))
		self.input_categoria.setItemText(5, self.tr(u"Filmes"))
		self.input_categoria.setItemText(6, self.tr(u"Frases"))
		self.input_categoria.setItemText(7, self.tr(u"Favoritos"))
		self.input_categoria.setItemText(8, self.tr(u"Objetos"))
		self.input_categoria.setItemText(9, self.tr(u"Textos"))
		self.input_categoria.setItemText(10, self.tr(u"Personagens"))

		self.input_categoria.setPlaceholderText(self.tr(u"Categoria"))
		self.icone_nome_desenho.setText(self.tr(u"Nome para o desenho Limitado (27)"))
		self.icone_categoria.setText(self.tr(u"Categoria (opcional)"))
		self.btn_p5.setText(self.tr(u"Concluir"))
		self.btn_voltar_c5.setText(self.tr(u"Voltar"))
		self.rotulo_c5.setText(self.tr(u"<html><head/><body><p><span style=\" font-size:12pt; font-weight:700;\">Hora de configurar desenho final adicionando o nome para o desenho etc</span></p></body></html>"))
		self.btn_ajuda_c5.setText(self.tr(u"Ajuda"))
		self.rotulo_c6.setText(self.tr(u"Carregando Aguarde..."))
		self.tela_resultado.setTitle(self.tr(u"Resultado Concluido"))
		self.rotulo_r.setText(self.tr(u"Concluido com sucesso"))
		self.icone3_cc6.setText(self.tr(u"Largura: None"))
		self.icone5_cc6.setText(self.tr(u"Fill Removido: None"))
		self.icone4_cc6.setText(self.tr(u"Densidade: None"))
		self.icone6_cc6.setText(self.tr(u"Otimizado: None"))
		self.icone1_cc6.setText(self.tr(u"Nome do Desenho: None"))
		self.icone2_cc6.setText(self.tr(u"Altura: None"))
		self.icone7_cc6.setText(self.tr(u"Finalizado: None"))
		self.btn_p6.setText(self.tr(u"Visualizar desenho"))
	# retranslateUi

	@Slot()
	def initTema(self):
		try:
			if CONFIG_TEMA[0] == "Dark":
				with open(LOCAL_TEMA_ESCURO_CAMELTRACE, 'r+') as abrir_tema:
					_str_tema = abrir_tema.read()
					self.setStyleSheet(_str_tema)
			else:
				with open(LOCAL_TEMA_CLARO_CAMELTRACE, 'r+') as abrir_tema:
					_str_tema = abrir_tema.read()
					self.setStyleSheet(_str_tema)
		except Exception as e:
			msg = Mensagem(self, QMessageBox.Critical, self.tr(u"Erro ao iniciar tema: ") + str(e), u"Erro", QMessageBox.Ok)
			msg.exec()


	@Slot()	
	def initTray(self):

		self.exibir_ac = QAction(self.tr(u"Exibir"), self)
		self.exibir_ac.setIcon(QIcon(u":/icones/Visivel.png"))
		self.exibir_ac.triggered.connect(self.showNormal)

		self.config_ac = QAction(self.tr(u"Configurações"), self)
		self.config_ac.setIcon(QIcon(u":/icones/Configurar.png"))
		self.config_ac.triggered.connect(lambda: CamelConfig(self))

		self.sair_ac = QAction(self.tr(u"Sair"), self)
		self.sair_ac.setIcon(QIcon(u":/icones/Desligar.png"))
		self.sair_ac.triggered.connect(self.close)

		self.tray_menu = QMenu()
		self.tray_menu.addAction(self.exibir_ac)
		self.tray_menu.addAction(self.config_ac)
		self.tray_menu.addSeparator()
		self.tray_menu.addAction(self.sair_ac)

		self.tray = QSystemTrayIcon(self)
		self.tray.activated.connect(self.ac_tray_ativado)
		self.tray.setIcon(self.icone_cameltrace_window)
		self.tray.setVisible(True)
		self.tray.setContextMenu(self.tray_menu)

	@Slot(str)
	def ac_tray_ativado(self, entrada = None):
		if entrada == QSystemTrayIcon.Trigger:
			self.showNormal()
		if entrada == QSystemTrayIcon.DoubleClick:
			pass

	@Slot(str, str, str)
	def ac_tray_msg(self, msg = None, body = None, icon = None):

		icon_body = QIcon(icon)
		self.tray.showMessage(str(msg), str(body), icon_body, 15 * 1000)

	@Slot(int)
	def ac_alterar_pagina(self, entrada):
		for btn in self.botoes_menu:
			try:
				btn.setAtivo(True) if entrada == btn.pagina else btn.setAtivo(False)
			except:
				pass
				
	@Slot(str)
	def ac_abrir_imagem(self, caminho = None):

		# ABRE O ARQUIVO DE IMAGEM E VERIFICA COMPARTIBILIDADE DE EXTENSOES

		self.caminho = caminho

		if not self.caminho:
			self.btn_p2.setEnabled(False)
		else:
			caminho_existe = QFile(self.caminho)
			if caminho_existe.exists() is True:
				if self.caminho.endswith((".jpg", ".gif", ".png", ".jpge", ".bmp", ".ico", ".webp", "mpeg", ".jfif", ".tiff", ".jpeg")):
					self.input_imagem.setText("")
					self.input_imagem.setToolButtonStyle(Qt.ToolButtonIconOnly)
					self.input_imagem.setStyleSheet(f"#input_imagem{{qproperty-icon: url({self.caminho}); qproperty-iconSize: 290px 290px;  padding-top: 0px;}}")
					self.btn_p2.setEnabled(True)
				else:
					msg = Mensagem(self, QMessageBox.Critical, self.tr(u"Erro: Não suportamos esse tipo de arquivo"), self.tr(u"Erro de compatibilidade"), QMessageBox.Ok)
					msg.exec()
			else:
				msg = Mensagem(self, QMessageBox.Critical, self.tr(u"Erro: Caminho da imagem nao existe"), self.tr(u"Erro de arquivo não existe"), QMessageBox.Ok)
				msg.exec()					 

	@Slot(int)
	def ac_temporario_1(self, filtro):

		# CRIA O ARQUIVO BMP TEMPORARIO EM UMA VAR GLOBAL

		global GLOBAL_BITMAP
		global GLOBAL_ALTURA
		global GLOBAL_LARGURA

		try:
			img_data = io.BytesIO()

			img_bmp = Image.open(self.caminho)
			GLOBAL_ALTURA = img_bmp.height
			GLOBAL_LARGURA = img_bmp.width

			if filtro == 1:
				self.rotulo_filtro.setText(self.tr(u"Filtro: Sem Filtro"))
			elif filtro == 2:
				img_bmp = img_bmp.filter(ImageFilter.DETAIL)
				self.rotulo_filtro.setText(self.tr(u"Filtro: Detalhado"))
			elif filtro == 3:
				img_bmp = img_bmp.filter(ImageFilter.EDGE_ENHANCE)
				self.rotulo_filtro.setText(self.tr(u"Filtro: Realçado"))
			else:
				pass
			img_bmp.save(img_data, "bmp")
			img_data.seek(0)
			GLOBAL_BITMAP = img_data.read()

			self.ac_temporario_2()

		except Exception as e:
			msg = Mensagem(self, QMessageBox.Critical, self.tr(u"Erro ao conveter imagem para Bitmap: ") + str(e), u"Erro", QMessageBox.Ok)
			msg.exec()

	def ac_temporario_2(self):
		
		# CRIA O ARQUIVO SVG TEMPORARIO EM UMA PASTA (LOCAL_TEMP_SVG)
		
		try:

			argumentos = ['potrace.exe'] + ["--flat"] + ["-s", "-", "-o-"]
			processo = subprocess.Popen(argumentos, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
			self.svg_temp, byt = processo.communicate(input=GLOBAL_BITMAP)
			self.ac_temporario_3(self.svg_temp)
		except Exception as e:
			msg = Mensagem(self, QMessageBox.Critical, self.tr(u"Erro ao conveter bitmap para Svg: ") + str(e), u"Erro", QMessageBox.Ok)
			msg.exec()

	def ac_temporario_3(self, entrada = None):

		# CRIA O ARQUIVO SVG COM FILL REMOVIDO USADO PARA PRÉ VISUALIZAÇÃO TEMPORARIO EM UMA PASTA (LOCAL_TEMP_SVG)
		
		try:
			string = entrada.decode("utf-8").replace('\n', ' ').replace('fill="#000000" stroke="none"', 'fill="none" stroke="#000000"').replace('<path', '<path vector-effect="non-scaling-stroke"')
			entrada_preview = bytes(string, encoding='utf-8')	

			pix1 = QPixmap()
			pix1.loadFromData(GLOBAL_BITMAP)
			pix1 = pix1.scaled(220, 220, Qt.KeepAspectRatio, Qt.SmoothTransformation)

			pix2 = QPixmap()
			pix2.loadFromData(entrada)
			pix2 = pix2.scaled(220, 220, Qt.KeepAspectRatio, Qt.SmoothTransformation)

			pix3 = QPixmap()
			pix3.loadFromData(entrada_preview)
			pix3 = pix3.scaled(220, 220, Qt.KeepAspectRatio, Qt.SmoothTransformation)

			self.img_bmp.setPixmap(pix1)
			self.img_svg.setPixmap(pix2)
			self.img_final.setPixmap(pix3)
			self.paginas.setCurrentIndex(3)

		except Exception as e:
			msg = Mensagem(self, QMessageBox.Critical, self.tr(u"Erro ao remover fill do Svg: ") + str(e), u"Erro", QMessageBox.Ok)
			msg.exec()

	def ac_pagina_resetar(self):
		try:
			self.icone_monitor.setText(self.tr(u"Tamanho da Tela") + str(f": ({GLOBAL_LARGURA_APP}x{GLOBAL_ALTURA_APP})"))
			self.icone_tamanho_img.setText(self.tr(u"Tamanho da Imagem") + str(f": ({GLOBAL_ALTURA}x{GLOBAL_LARGURA})"))
		except:
			...

		self.input_nome_desenho.clear()
		self.input_proporcao.setChecked(True)
		self.input_altura.setValue(0)
		self.input_altura.setValue(400)

		self.paginas.setCurrentIndex(4)

	def ac_proporcao_altura(self, entrada):

		global PROPORCAO_ESTADO

		if self.input_proporcao.isChecked() == True:
			if PROPORCAO_ESTADO == 'LARGURA':
				...
			else:
				PROPORCAO_ESTADO = 'ALTURA'
				nova_altura = entrada
				multi = nova_altura / GLOBAL_ALTURA
				nova_largura = GLOBAL_LARGURA * multi
				self.input_largura.setValue(int(nova_largura))
				PROPORCAO_ESTADO = None


	@Slot(int)		 
	def ac_proporcao_largura(self, entrada):

		global PROPORCAO_ESTADO

		if self.input_proporcao.isChecked() == True:
			if PROPORCAO_ESTADO == 'ALTURA':
				...
			else:
				PROPORCAO_ESTADO = 'LARGURA'
				nova_largura = entrada
				multip = nova_largura / GLOBAL_LARGURA
				nova_altura = GLOBAL_ALTURA * multip
				self.input_altura.setValue(int(nova_altura))
				PROPORCAO_ESTADO = None

	def ac_verificar(self):
		self.tamanho_altura = int(self.input_altura.text())
		self.tamanho_largura = int(self.input_largura.text())
		self.nome_desenho = self.input_nome_desenho.text()
		self.categoria = self.input_categoria.currentText()
		if self.nome_desenho == "":
			msg = Mensagem(self, QMessageBox.Warning, self.tr(u"Atenção adicione um nome para o desenho"), self.tr(u"Atenção"), QMessageBox.Ok)
			msg.exec()
		else:
			self.setValores()

	def setValores(self):

		self.hash_string = str(randint(100000,1000000))
		self.nome_arquivos =  'CMDW' + self.hash_string

		self.local_svg = os.path.join(LOCAL_SVG, f"{self.nome_arquivos}.svg")
		self.local_svg_branco = os.path.join(LOCAL_SVG, f"{self.nome_arquivos}_b.svg")
		self.local_linha = os.path.join(LOCAL_LINHAS, f"{self.nome_arquivos}.clines")
		self.local_json = os.path.join(LOCAL_JSON, f"{self.nome_arquivos}.json")
		self.local_json_exist = os.path.exists(self.local_json)

		if self.local_json_exist == False:
			self.ac_preparar()
		else:
			return self.setValores()

	@Slot()
	def ac_preparar(self):
		try:
			self.btn_p6.setEnabled(False)
			self.tela_menu.setEnabled(False)
			self.tela_cc6.hide()
			self.btn_p6.setEnabled(False)
			self.tela_c6.show()
			self.paginas.setCurrentIndex(5)
			self.movie = QMovie('data/recursos/icones/Carregamento_Camellost.gif')
			self.movie.setScaledSize(QSize(150,150))
			self.movie.setCacheMode(QMovie.CacheAll)
			self.movie.setSpeed(128)
			self.movie.start()
			self.gif_carregamento.setMovie(self.movie)
			self.barra_estado.showMessage(self.tr(u"Iniciado"), 2000)
			self.thread = threading.Thread(target=self.initTHREAD)
			self.thread.daemon = True
			self.thread.start()
		except Exception as e:
			msg = Mensagem(self, QMessageBox.Warning, self.tr(u"Erro Inesperado: ") + str(e), u"Erro", QMessageBox.Ok)
			msg.exec()

	def initTHREAD(self):
		try:
			self.rotulo_c6.setText(self.tr(u"Convertendo..."))

			argumentos = f'potrace.exe -s -H {self.tamanho_altura}.0pt -W {self.tamanho_largura}.0pt -o {self.local_svg} {ARGUMENTOS}' if ARGUMENTOS is not None else f'potrace.exe -s -H {self.tamanho_altura}.0pt -W {self.tamanho_largura}.0pt -o {self.local_svg} --flat'
			processo = subprocess.Popen(argumentos, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
			processo.communicate(input=GLOBAL_BITMAP)

			self.ac_otimizar()
		except Exception as e:
			self.rotulo_c6.setText(self.tr(u"Falha ao Converter (Reinicie o CamelTrace)..."))
			self.ac_tray_msg(self.tr(u"Erro ao conveter bitmap para Svg"), self.tr(u"Erro ao conveter bitmap para Svg: ") + str(e), u":/icones/Cancelar.png")

	def ac_otimizar(self):

		try:
			self.rotulo_c6.setText(self.tr(u"Otimizando..."))
			argumentos2 = f'svgo-win.exe -i {self.local_svg} -o {self.local_svg}'
			processo2 = subprocess.Popen(argumentos2, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
			processo2.communicate()

			self.ac_remover_fill()
		except Exception as e:
			self.rotulo_c6.setText(self.tr(u"Falha na otimização (Reinicie o CamelTrace)..."))
			self.ac_tray_msg(self.tr(u"Erro ao otimizar Svg"), self.tr(u"Erro ao otimizar Svg: ") + str(e), u":/icones/Cancelar.png")


	def ac_remover_fill(self):
		try:
			self.rotulo_c6.setText(self.tr(u"Removendo Fill Adicionando Stroke..."))

			with open(self.local_svg, 'r+') as abrir_svg:
				data = abrir_svg.read()
				search_height = re.findall(r'height="[a-zA-Z0-9.]+"', data)
				search_width = re.findall(r'width="[a-zA-Z0-9.]+"', data)

			if search_height and search_width:
				for width in search_width:
					data = data.replace(width, f'width="{self.tamanho_largura}"')
				for height in search_height:
					data_b = data.replace(height, f'height="{self.tamanho_altura}" fill="none" stroke="#dedede"')
					data = data.replace(height, f'height="{self.tamanho_altura}" fill="none" stroke="#000"')

				with open(self.local_svg, 'w+') as salvar_svg:
					salvar_svg.write(data)
				with open(self.local_svg_branco, 'w+') as salvar_svg_b:
					salvar_svg_b.write(data_b)

				self.ac_criar_coordenadas()
			else:
				raise Exception(self.tr(u"Erro: ao encontrar elementos height, width no Svg"))
		except Exception as e:
			self.rotulo_c6.setText(self.tr(u"Falha ao remover Fill (Reinicie o CamelTrace)"))
			self.ac_tray_msg(self.tr(u"Erro ao remover fill do Svg"), self.tr(u"Erro ao remover fill do Svg: ") + str(e), u":/icones/Cancelar.png")

	@Slot()
	def ac_criar_coordenadas(self):
		try:
			self.inicio_tempo = time.time()

			with open(self.local_svg, 'r') as abrir_svg:
				self.svg_path = abrir_svg.read()

			self.rotulo_c6.setText(self.tr(u"Procurando Caminho..."))

			strings = re.findall(r'<path d="([ A-Za-z0-9\., -]+)"', self.svg_path)
			paths = []
			self.pts = []

			if strings:
				self.rotulo_c6.setText(self.tr(u"Analisando Caminho..."))

				for string in strings:
					paths.append(Path(string))

				# paths[1] se a mais elementos "<path d=" no caminho svg.


				if self.input_manual.isChecked() == True:
					self.velocidade = self.input_densidade.text()
					self.vel = "Manual"
				else:
					if self.input_lento.isChecked() == True:
						self.vel = "Lento"
						porc = 0.30
					elif self.input_normal.isChecked() == True:
						self.vel = "Normal"
						porc = 0.00
					elif self.input_rapido.isChecked() == True:
						self.vel = "Rapido"
						porc = 0.50
					elif self.input_mt_rapido.isChecked() == True:
						self.vel = "Muito Rapido"
						porc = 0.70
					else:
						...

					# se a mais + paths em elementos "d" for path in paths loop conta

					strings_path = paths[0]

					self.comprimento = int(strings_path.length())
					self.porcentagem = int(self.comprimento * porc)


					if self.vel == "Lento":
						self.velocidade = self.comprimento + self.porcentagem
					else:
						self.velocidade = self.comprimento - self.porcentagem


				n = int(self.velocidade) 

				for path in paths:
					self.pt = []
					self.rotulo_c6.setText(self.tr(u"Criando Pontos Aguarde... (1/1)"))
					for i in range(0, n+1):
						f = i/n
						complexo = path.point(f)
						self.pt.append((complexo.real, complexo.imag))
					self.pts.append(self.pt)

				self.ac_salvar_desenho()

			else:
				raise Exception(self.tr(u"Nenhum ponto no svg foi encontrado (Reinicie o CamelTrace)"))
		except Exception as e:
			self.rotulo_c6.setText(self.tr(u"Houve um erro inesperado (Reinicie o CamelTrace)"))
			self.ac_tray_msg(self.tr(u"Houve um erro inesperado"), self.tr(u"Houve um erro inesperado: ") + str(e), u":/icones/Cancelar.png")

	@Slot()
	def ac_salvar_desenho(self):

		try:
			self.rotulo_c6.setText(self.tr(u"Salvando..."))

			with open(self.local_linha, "wb") as salvar_linhas:
				dump(self.pts, salvar_linhas)

			self.data_criado = str(time.strftime("%a, %d %B %Y", time.gmtime()))
			self.horas_criado = str(time.strftime('%X'))

			self.data_json = {'Nome_Desenho': str(self.nome_desenho),
			'Tamanho_Altura': int(self.tamanho_altura),
			'Tamanho_Largura': int(self.tamanho_largura),
			'Tamanho_Pontos': int(self.velocidade),
			'Local_Svg': str(self.local_svg),
			'Local_Svg_b': str(self.local_svg_branco),
			'Local_Lines': str(self.local_linha),
			'Data_Criado': self.data_criado,
			'Horas_Criado': self.horas_criado,
			'Tempo': "",
			'Categoria': str(self.categoria),
			'Trancado': False,
			'Trancado_Senha': "",
			'Velocidade': self.vel
			}
			with open(self.local_json, 'w', encoding='utf-8') as salvar_json:
				json.dump(self.data_json, salvar_json, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))

			resultado_tempo = time.time() - self.inicio_tempo
			resultado_tempo = time.strftime("%H:%M:%S", time.gmtime(resultado_tempo))

			self.icone1_cc6.setText(f'Nome do Desenho: {self.nome_desenho}')
			self.icone2_cc6.setText(f'Altura: {self.tamanho_altura}')
			self.icone3_cc6.setText(f'Largura: {self.tamanho_largura}')
			self.icone4_cc6.setText(f'Pontos: {self.velocidade} - ({self.vel})')
			self.icone5_cc6.setText(f'Fill Removido: OK')
			self.icone6_cc6.setText(f'Otimizado: OK')
			self.icone7_cc6.setText(f'Finalizado: {resultado_tempo}')

			self.tela_c6.hide()
			self.tela_cc6.show()
			self.btn_p6.setEnabled(True)
			self.movie.stop()

			ARGUMENTOS = None

			self.ac_tray_msg("Desenho Finalizado!", f"O Desenho {self.nome_desenho} foi finalizado com sucesso!\nTempo: {resultado_tempo}", u":/icones/Concluido.png")
		
		except Exception as e:
			self.rotulo_c6.setText(self.tr(u"Houve um erro ao salvar o desenho (Reinicie o CamelTrace)"))
			self.ac_tray_msg(self.tr(u"Houve um erro ao salvar o desenho"), self.tr(u"Houve um erro inesperado: ") + str(e), u":/icones/Cancelar.png")

	def ac_carregar_novo(self):

		self.ac_carregar_desenhos()
		self.tela_menu.setEnabled(True)
		self.paginas.setCurrentIndex(0)

	def ac_carregar_desenhos(self):

		global TOTAL_DESENHO

		self.desenhos = []

		for root, dirs, arquivos in os.walk(LOCAL_JSON):
			for arquivo in arquivos:
				if arquivo.endswith(".json"):
					local = os.path.join(LOCAL_JSON, arquivo)
					self.desenhos.append(local)
				else:
					...
		self.lista_conteudo.clear()

		TOTAL_DESENHO = int(len(self.desenhos))
		self.rotulo_pesquisas.setText(self.tr(u"Meus Desenhos - ") + str(TOTAL_DESENHO))

		if self.desenhos:
			self.tela_vazia.hide()
			self.lista_conteudo.show()
			for desenho in self.desenhos:
				with open(desenho) as abri_json:
					ler_json = json.load(abri_json)
					op1 = ler_json['Nome_Desenho']
					op2 = ler_json['Tamanho_Altura']
					op3 = ler_json['Tamanho_Largura']
					op4 = ler_json['Tamanho_Pontos']
					op5 = ler_json['Local_Svg']
					op6 = ler_json['Local_Lines']
					op7 = ler_json['Data_Criado']
					op8 = ler_json['Horas_Criado']
					op9 = ler_json['Tempo']
					op10 = ler_json['Categoria']
					op11 = ler_json['Trancado']
					op12 = ler_json['Trancado_Senha']
					op13 = ler_json['Velocidade']
					op14 = ler_json['Local_Svg_b']

					conteudo = CamelDesenho(self, op1, op2, op3, op4, op5, op6, desenho, op7, op8, op9, op10, op11, op12, op13, op14)
					item = QListWidgetItem()
					item.setTextAlignment(Qt.AlignHCenter)
					self.lista_conteudo.insertItem(self.lista_conteudo.count(), item)
					self.lista_conteudo.setItemWidget(item, conteudo)
					item.setSizeHint(conteudo.sizeHint())


		else:
			self.tela_vazia.show()
			self.lista_conteudo.hide()
			self.rotulo_pesquisas.setText(self.tr(u"Nenhum desenho encontrado!"))

	@Slot(str)
	def ac_pesquisar(self, texto):

		total = 0

		for row in range(self.lista_conteudo.count()):
			itens = self.lista_conteudo.item(row)
			conteudo = self.lista_conteudo.itemWidget(itens)
			if texto:
				itens.setHidden(not self.filter(texto, conteudo.nome, conteudo.categoria))
				if self.filter(texto, conteudo.nome, conteudo.categoria):
					total +=1
			else:
				itens.setHidden(False)
		if total == 0:
			self.rotulo_pesquisas.setText(self.tr(u"Nenhum desenho encontrado :("))
		else:
			self.rotulo_pesquisas.setText(str(total) + self.tr(u" Desenho encontrado"))
		if self.input_pesquisar.text() == "":
			self.rotulo_pesquisas.setText(self.tr(u"Meus Desenhos - ") + str(TOTAL_DESENHO))


	def filter(self, text, keywords, keywords2):
		if self.input_categorias.currentIndex() == 0:
			return str(text.upper()) in str(keywords.upper())
		else:
			return str(text.upper()) in str(keywords.upper()) and keywords2 == self.input_categorias.currentText()

	def ac_sobre(self):
		self.caixa_sobre = QDialog(self)
		self.caixa_sobre.setObjectName(u"Sobre")
		self.caixa_sobre.resize(440, 285)
		self.caixa_sobre.setMinimumSize(QSize(440, 285))
		self.caixa_sobre.setMaximumSize(QSize(440, 285))
		self.caixa_sobre.setWindowTitle(self.tr(u"Sobre CamelTrace"))
		self.verticalLayout = QVBoxLayout(self.caixa_sobre)
		self.verticalLayout.setObjectName(u"verticalLayout")
		self.verticalLayout.setContentsMargins(0, 0, 0, 0)
		self.tela_sobre_l = QFrame(self.caixa_sobre)
		self.tela_sobre_l.setObjectName(u"tela_sobre_l")
		self.horizontalLayout = QHBoxLayout(self.tela_sobre_l)
		self.horizontalLayout.setSpacing(0)
		self.horizontalLayout.setObjectName(u"horizontalLayout")
		self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
		self.logo_cameltrace_sobre = QPushButton(self.tela_sobre_l)
		self.logo_cameltrace_sobre.setObjectName(u"logo_cameltrace_sobre")
		self.horizontalLayout.addWidget(self.logo_cameltrace_sobre)
		self.verticalLayout.addWidget(self.tela_sobre_l)
		self.frame = QFrame(self.caixa_sobre)
		self.frame.setObjectName(u"frame")
		self.frame.setFrameShape(QFrame.StyledPanel)
		self.frame.setFrameShadow(QFrame.Raised)
		self.verticalLayout_2 = QVBoxLayout(self.frame)
		self.verticalLayout_2.setObjectName(u"verticalLayout_2")
		self.label = QLabel(self.frame)
		self.label.setObjectName(u"label")
		self.label.setWordWrap(True)
		self.label.setOpenExternalLinks(True)
		self.label.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)
		self.label.setText(self.tr(u"<html><head/><body><p>CamelTrace - Criação e automatização de desenhos com o mouse! </p><p>Versão 2.12 (x64) - 2022 Camellost</p><p>Autor: Emerson Maciel - MagioZ - Github <a href=\"https://github.com/Camellost/CamelTrace\"><span style=\" text-decoration: underline; color:#3079d6;\">CamelTrace</span></a></p><p>Contato: Camellost.rf.gd@gmail.com </p><p>Agradecimento Ícones de <a href=\"https://icons8.com/\"><span style=\" text-decoration: underline; color:#3079d6;\">icons8.com </span></a></p><p><span style=\" font-style:italic; color:#707070;\">CamelTrace foi criado para fins educativos não lucrativos</span></p></body></html>"))
		self.verticalLayout_2.addWidget(self.label)
		self.line = QFrame(self.frame)
		self.line.setObjectName(u"line")
		self.line.setFrameShadow(QFrame.Plain)
		self.line.setFrameShape(QFrame.HLine)
		self.verticalLayout_2.addWidget(self.line)
		self.buttonBox = QDialogButtonBox(self.frame)
		self.buttonBox.setObjectName(u"buttonBox")
		self.buttonBox.setOrientation(Qt.Horizontal)
		self.buttonBox.setStandardButtons(QDialogButtonBox.Ok)
		self.verticalLayout_2.addWidget(self.buttonBox)
		self.verticalLayout.addWidget(self.frame)

		self.buttonBox.accepted.connect(self.caixa_sobre.accept)
		self.buttonBox.rejected.connect(self.caixa_sobre.reject)
		QMetaObject.connectSlotsByName(self.caixa_sobre)

		self.caixa_sobre.exec()

	def ac_ajuda(self):
		msg = Mensagem(self, QMessageBox.Information, self.tr(u"<html><head/><body><p>1° Velocidade do desenho pode ser ajustada, conforme o valor da densidade.</p><p>2° A densidade resulta na quantidade de pontos ou traços do SVG</p><p>3° Quanto menor o valor da densidade maior será a velocidade e menor será a quantidade de pontos podendo perder mais a qualidade do desenho</p><p>4° Velocidade normal resulta no valor padrão de densidade.</p><p>5° Desenho distorcido diferente da imagem original, você pode corrigir ativando a caixa de opção &quot;Manter proporção&quot; sendo redimensionada na largura ou altura evitando distorção</p></body></html>"), self.tr(u"Ajuda rapida"), QMessageBox.Ok)
		msg.exec()

	def ac_liberar_memoria(self):
		liberar = liberar_memoria()
		if liberar == True:
			msg = Mensagem(self, QMessageBox.Information, self.tr(u"Memória Liberada"), self.tr(u"Otimizado"), QMessageBox.Ok)
			msg.exec()

	@Slot()
	def ac_cor_fundo(self):
		abrir_dialog = QColorDialog.getColor(options=QColorDialog.ShowAlphaChannel)
		if abrir_dialog.isValid():
			cor_fundo = str(abrir_dialog.name(QColor.HexArgb))
			self.lista_conteudo.setStyleSheet(f"""
	#conteudo_desenho{{
		background-color: {cor_fundo};
		border-radius: 5px;
}}""")

	def ac_esconder_imagem(self, entrada):
		if entrada == True:
			total = 0
			for row in range(self.lista_conteudo.count()):
				it = self.lista_conteudo.item(row)
				conteudo = self.lista_conteudo.itemWidget(it)
				conteudo.ac_ocultar()
		else:
			total = 0
			for row in range(self.lista_conteudo.count()):
				it = self.lista_conteudo.item(row)
				conteudo = self.lista_conteudo.itemWidget(it)
				conteudo.ac_exibir()

	def ac_mode_grade(self):
		self.btn_modo.setStyleSheet("""
#btn_modo{
	qproperty-icon: url(:/icones/Grade.png);
	qproperty-iconSize: 20px 20px;
}
			""")
		self.lista_conteudo.setViewMode(QListView.IconMode)
	def ac_mode_fileira(self):
		self.btn_modo.setStyleSheet("""
#btn_modo{
	qproperty-icon: url(:/icones/Fileira.png);
	qproperty-iconSize: 20px 20px;
}
			""")
		self.lista_conteudo.setViewMode(QListView.ListMode)
		self.lista_conteudo.setProperty("showDropIndicator", False)

if __name__ == '__main__':
	try:
		app = QApplication(sys.argv)

		# REMOVE ANIMACAO DO COMBOBOX

		QApplication.setEffectEnabled(Qt.UI_AnimateCombo, False)

		# TRAVA A EXECUCAO DO APP EM SEGUNDA ESTÂNCIA EM exec.lock AO FINALIZAR O CAMELTRACE DESTRAVA
		# qt_path_locale = QLibraryInfo.location(QLibraryInfo.TranslationsPath)

		lock_file = QLockFile("exec.lock")

		qt_translator = QTranslator()
		qt_translator.load(f"{LOCAL_IDIOMAS}{QLocale.system().name()}.qm")
		app.installTranslator(qt_translator)
		
		if lock_file.tryLock():
			try:
				config = Criador_Config_Pasta()
				config.ac_verificar_pasta()
			except Exception as e:
				QMessageBox.warning(None, u"Erro ao criar pasta e configurações", f"Erro ao criar pasta e configurações: {e}")

			try:
				locale = QLocale()
				GLOBAL_LARGURA_APP, GLOBAL_ALTURA_APP = pyautogui.size()
				camel_win = CamelTrace()
				camel_win.initTema()
				camel_win.initTray()
				camel_win.ac_carregar_desenhos()
				camel_win.setLocale(locale)
				camel_win.show()
			except Exception as e:
				QMessageBox.warning(None, u"Erro CamelTrace", u"Erro CamelTrace: " + str(e))
			sys.exit(app.exec())
		else:
			QMessageBox.warning(None, u"Em execução", u"CamelTrace está em execução.")
	finally:
		lock_file.unlock()





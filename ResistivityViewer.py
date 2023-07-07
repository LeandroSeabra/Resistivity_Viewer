"""
Nome do Arquivo: ResistivityViewer.py
Autor: Leandro Seabra Moreira
Data da Última Modificação: 07/07/2023

Descrição: Este programa é destinado à visualização de conjuntos de dados de resistividade 3D. 
Ele realiza a leitura dos dados, gera um arquivo XYZR  e cria visualizações de diferentes planos dos dados, 
além de um gráfico 3D, usando as bibliotecas plotly e Mayavi. 

Atualizações: 
- Refatoração do código para uma abordagem POO.

Variáveis:
- filepar: Caminho para o arquivo que contém os dados de resistividade.
- filexbl, fileybl, filezbl: Caminhos para os arquivos que contêm as coordenadas x, y, z.

Classes e Métodos: 
    - DataProcessor: Classe para processamento dos dados iniciais.
    - __init__: Método construtor que inicializa os caminhos dos arquivos e chama o método para processar os dados.
    - process_data: Método que chama os métodos para obter as dimensões, coordenadas e parâmetros dos dados.
    - get_dimensions: Método para obter as dimensões dos dados.
    - get_coordinates: Método para obter as coordenadas dos dados.
    - get_parameters: Método para obter os parâmetros dos dados.

- XYZGenerator: Classe para gerar o arquivo XYZ a partir dos dados processados.

- PlotGenerator: Classe para criar visualizações 2D dos dados.
    - plot_xy: Método para plotar os dados no plano xy
    - plot_xz: Método para plotar os dados no plano xz.
    - plot_yz: Método para plotar os dados no plano yz

- MayaviPlotter: Classe para criar a visualização 3D dos dados usando a biblioteca Mayavi.
    - plot_xyz: Método para plotar os dados no espaço 3D
    
Atualização futura:  Plot 2D apenas com arquivo xyz, melhorar saida dos graficos (vizualização, labels), criar metodo plot convergência
----------------------------------------------------------------------------------------
"""

import numpy as np
import plotly.subplots as sp
import plotly.graph_objects as go
import os
from mayavi import mlab

class DataProcessor:

    def __init__(self, filepar, filexbl, fileybl, filezbl):
        self.filepar = filepar
        self.filexbl = filexbl
        self.fileybl = fileybl
        self.filezbl = filezbl
        self.process_data()

    def process_data(self):
        self.get_dimensions()
        self.get_coordinates()
        self.get_parameters()

    def get_dimensions(self):
        with open(self.filexbl, 'r') as fx:
            self.npx = len(list(fx)) - 1
        with open(self.fileybl, 'r') as fy:
            self.npy = len(list(fy)) - 1
        with open(self.filezbl, 'r') as fz:
            self.npz = len(list(fz)) - 1

    def get_coordinates(self):
        self.x, self.y, self.z = [], [], []
        with open(self.filexbl, 'r') as cx:
            self.x = [float(line.split()[0])/1000 for line in cx]
        with open(self.fileybl, 'r') as cy:
            self.y = [float(line.split()[0])/1000 for line in cy]
        with open(self.filezbl, 'r') as cz:
            self.z = [float(line.split()[0])/1000 for line in cz]

    def get_parameters(self):
        with open(self.filepar, 'r') as cP:
            self.P = [float(line.split()[0]) for line in cP]


class XYZGenerator:

    def __init__(self, data_processor):
        self.data_processor = data_processor
        self.generate_xyz()

    def generate_xyz(self):
        nuvem_pontos = []
        for k in range(self.data_processor.npz):
            for j in range(self.data_processor.npy):
                for i in range(self.data_processor.npx):
                    ind = (k) * self.data_processor.npx * self.data_processor.npy + (j) * self.data_processor.npx + i
                    X = self.data_processor.x[i]
                    Y = self.data_processor.y[j]
                    Z = self.data_processor.z[k]
                    resistivity_value = self.data_processor.P[ind]
                    nuvem_pontos.append([X, Y, Z, resistivity_value])
        np.savetxt('nuvem_pontos.xyz', nuvem_pontos, fmt='%1.3f', delimiter='\t')


class PlotGenerator:

    def __init__(self, data_processor):
        self.data_processor = data_processor
         # Melhorar essa parte !
        self.nl = 5                                        
        self.nc = 3
        self.fig_height = 200
        self.min_val = int(np.min(self.data_processor.P))
        self.max_val = int(np.max(self.data_processor.P))

    def plot_xyz(self):
        self.plot_xy()
        self.plot_xz()
        self.plot_yz()

    def plot_xy(self):
        fig_xy = sp.make_subplots(rows=self.nl, cols=self.nc)
        for k in range(self.data_processor.npz):
            data_plane_xy = np.empty((self.data_processor.npy, self.data_processor.npx))
            for j in range(self.data_processor.npy):
                for i in range(self.data_processor.npx):
                    ind = k * self.data_processor.npx * self.data_processor.npy + j * self.data_processor.npx + i
                    data_plane_xy[j][i] = self.data_processor.P[ind]
            fig_xy.add_trace(go.Heatmap(z=data_plane_xy, x=self.data_processor.x[:self.data_processor.npx], y=self.data_processor.y[:self.data_processor.npy], coloraxis="coloraxis"), row=(k//self.nc)+1, col=(k%self.nc)+1)
        fig_xy.update_layout(height=self.fig_height*self.nl, coloraxis=dict(colorscale='Jet', cmin=self.min_val, cmax=self.max_val), title_text="Plano XY (km), rho (Ohm.m)")
        fig_xy.update_yaxes(autorange="reversed")
        fig_xy.show()

    def plot_xz(self):
        fig_xz = sp.make_subplots(rows=self.nl, cols=self.nc)
        for j in range(self.data_processor.npy):
            data_plane_xz = np.empty((self.data_processor.npz, self.data_processor.npx))
            for k in range(self.data_processor.npz):
                for i in range(self.data_processor.npx):
                    ind = k * self.data_processor.npx * self.data_processor.npy + j * self.data_processor.npx + i
                    data_plane_xz[k][i] = self.data_processor.P[ind]
            fig_xz.add_trace(go.Heatmap(z=data_plane_xz, x=self.data_processor.x[:self.data_processor.npx], y=self.data_processor.z[:self.data_processor.npz], coloraxis="coloraxis"), row=(j//self.nc)+1, col=(j%self.nc)+1)
        fig_xz.update_layout(height=self.fig_height*self.nl, coloraxis=dict(colorscale='Jet', cmin=self.min_val, cmax=self.max_val), title_text="Plano XZ (km), rho (Ohm.m)")
        fig_xz.update_yaxes(autorange="reversed")
        fig_xz.show()

    def plot_yz(self):
        fig_yz = sp.make_subplots(rows=self.nl, cols=self.nc)
        for i in range(self.data_processor.npx):
            data_plane_yz = np.empty((self.data_processor.npz, self.data_processor.npy))
            for k in range(self.data_processor.npz):
                for j in range(self.data_processor.npy):
                    ind = k*self.data_processor.npx*self.data_processor.npy + j*self.data_processor.npx + i
                    data_plane_yz[k][j] = self.data_processor.P[ind]
            fig_yz.add_trace(go.Heatmap(z=data_plane_yz, x=self.data_processor.y[:self.data_processor.npy], y=self.data_processor.z[:self.data_processor.npz], coloraxis="coloraxis"), row=(i//self.nc)+1, col=(i%self.nc)+1)
        fig_yz.update_layout(height=self.fig_height*self.nl, coloraxis=dict(colorscale='Jet', cmin=self.min_val, cmax=self.max_val), title_text="Plano YZ (km), rho (Ohm.m)")
        fig_yz.update_yaxes(autorange="reversed")
        fig_yz.show()


class MayaviPlotter:

    def __init__(self, file_xyz):
        self.file_xyz = file_xyz

    def plot_xyz(self):
        data = np.loadtxt(self.file_xyz)
        x = data[:, 0]
        y = data[:, 1]
        z = data[:, 2]
        resistivity = data[:, 3]
        fig = mlab.figure()
        mlab.points3d(x, y, z, resistivity, colormap='jet', scale_mode='none')
        mlab.colorbar(orientation='vertical')
        mlab.show()




#principal


# Uso para classes acima

filepar = os.path.join('.', 'src', 'mod_estim.dat')
filexbl = os.path.join('.', 'src', 'xblc.dat')
fileybl = os.path.join('.', 'src', 'yblc.dat')
filezbl = os.path.join('.', 'src', 'zblc.dat')


# Processando os dados
data_processor = DataProcessor(filepar, filexbl, fileybl, filezbl)

# Gerando arquivo XYZ
xyz_generator = XYZGenerator(data_processor)

# Gerando os gráficos
plot_generator = PlotGenerator(data_processor)
plot_generator.plot_xyz()

# Plotando o arquivo XYZ com Mayavi
mayavi_plotter = MayaviPlotter('nuvem_pontos.xyz')
mayavi_plotter.plot_xyz()

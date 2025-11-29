# 🧠🧟 THE LAST SURVIVOR – Q-Learning Survival Game

Um jogo 2D feito em **Python + Pygame**, onde um agente controlado por **Inteligência Artificial (Q-Learning)** precisa **coletar suprimentos**, **desviar de zumbis**, **evitar pedras** e **sobreviver** até alcançar a zona segura.

A IA aprende sozinha a tomar decisões ideais!

---

## ⭐ Badges

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Pygame](https://img.shields.io/badge/Pygame-2.5-green)
![IA](https://img.shields.io/badge/IA-Q--Learning-orange)
![Status](https://img.shields.io/badge/Status-Finalizado-success)

---

## 📌 Sobre o Projeto

**The Last Survivor – RL** é um ambiente interativo onde um agente precisa:

✔ Coletar 5 suprimentos  
✔ Fugir dos zumbis  
✔ Desviar das pedras  
✔ Encontrar a zona segura  
✔ E principalmente: **aprender com erros e recompensas**

Esse projeto demonstra na prática:

- Reforço de aprendizado (Reinforcement Learning)  
- Q-Learning aplicado em ambientes 2D  
- Uso de tabelas Q (Q-Table)  
- Treinamento interativo  
- IA jogando automaticamente após aprender  

---

## 🧩 Funcionalidades

### 🟦 Mapa Aleatório (fixo por execução)
O mapa é gerado **uma única vez**, sempre no início, contendo:

- 1 agente  
- 1 zona segura  
- 4 zumbis  
- 5 suprimentos  
- 5 pedras  

### 🤖 IA com Q-Learning
- Exploração com ε-greedy  
- Decaimento automático do epsilon  
- Atualização constante da Q-Table  
- Salvamento e carregamento da Q-Table  

### 🎯 Objetivo da IA
A IA **só vence** quando:

1. Coleta todos os suprimentos  
2. Chega à zona segura  

---

## 🕹️ Como Jogar

### **Menu Inicial**
- **A** → IA jogar com modelo treinado  
- **T** → Treinar IA  
- **ESC** → Voltar ao menu durante o jogo  

---

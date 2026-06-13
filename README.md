# Calculadora de Gold para Aika BR (v2.0) 💰

Uma ferramenta de código aberto (open-source) feita em Python para ajudar a comunidade do **Aika Online (Aika BR)** a calcular com precisão cirúrgica seus lucros no mercado, planejar manufaturas de couro e simular faturamentos de farm na Estrada Espiral em tempo real.

| ☀️ Tema Claro | 🌙 Tema Escuro | 🎲 Simulação de Drop |
| :---: | :---: | :---: |
| <img width="310" alt="Tema Claro" src="https://github.com/user-attachments/assets/510299bf-06d6-471b-b5a1-fbf0ffa00a73" /> | <img width="310" alt="Tema Escuro" src="https://github.com/user-attachments/assets/ef42d36e-fe1a-4c05-a971-a70c5a908ec2" /> | <img width="310" alt="Simulação de drop" src="https://github.com/user-attachments/assets/8ffc32fa-ca6b-4d54-8bbe-7660bcf8f56a" /> |

---

## 🌟 Funcionalidades

- **Análise de Faturamento com Proporções:** Saiba instantaneamente o peso financeiro de cada drop! O programa exibe em tempo real a porcentagem que cada item representa no lucro bruto total, destacando o item mais valioso (**▲ em verde**) e o menos valioso (**▼ em laranja/vermelho**).
- **Estratégia de Manufatura Inteligente:** Simule o craft de *Couro Cristalino Pesado* para *Rígido*. O sistema calcula as colas necessárias (ajustadas pela taxa de compra), desconta a taxa de 10g do jogo e tranca os inputs (mostrando suas sobras reais), revelando se a estratégia dará lucro ou prejuízo.
- **Simulador Real de Drops por Tempo:** Estime seus ganhos de **Gold por Hora** e **Gold por Run** com base em um banco de dados real e empírico de drops coletados na Estrada Espiral.
- **Mecânica de Relíquias Atualizada:** Simulação completa de bônus integrando as Chaves Rivera e Morfhis (Lvl 1=5%, Lvl 2=10%, Lvl 3=15%), Bênção de Aika (+30%), Item Consumível (+30% Max) e o bônus de 15% de amplificação da Relíquia Valente!
- **Algoritmo de Busca por Proximidade:** Caso você configure uma taxa de drop que ainda não tenhamos dados exatos (ex: 94%), o sistema busca automaticamente a faixa mais próxima (ex: 90%) e emite um aviso em formato de pop-up.
- **Dual Theme (Claro e Escuro):** Alternância de temas fluida e moderna por um disjuntor `[ ☀️ | 🌙 ]` que atualiza a interface e a cor de título nativa do Windows 10/11.
- **Cadastrar e Deletar Itens:** Personalize a sua própria lista de itens salvando-os de forma persistente e segura no seu computador.

---

## 📥 Como Baixar e Usar

**Opção 1: Arquivo Executável (.exe) - Mais fácil**
1. Vá na aba de [Releases](https://github.com/Shimusin/calculadura-de-golds-estrada-espiral-aika-br/releases) aqui do lado direito do repositório.
2. Baixe o arquivo `calculadora_gold.exe`.
3. É só abrir e usar! (Não precisa instalar nada e já vem com ícone de gold embutido).
   
*Nota: Como é um programa feito de fã para fã e sem um certificado digital pago, o Windows Defender pode dar um aviso de "Software Desconhecido" na primeira abertura. Basta clicar em "Mais informações" > "Executar assim mesmo".*

**Opção 2: Rodar pelo Código-Fonte (Para programadores)**
1. Baixe os arquivos deste repositório.
2. Certifique-se de ter o Python 3 instalado.
3. Abra o terminal na pasta e execute:
```bash
python calculadora_gold.py
```

## 🛡️ Transparência e Privacidade
Este repositório é totalmente público para que toda a comunidade possa auditar o código-fonte do programa. Ele é seguro, não altera ou interfere em nenhum arquivo de segurança do jogo.

**Nota de Conexão à Internet:** Para manter sua proposta inicial de ser uma ferramenta leve e segura, o programa funciona **100% offline**. Ele realizará conexões externas **única e exclusivamente de forma sob demanda** ao acessar a aba *Simular Drops*, com o único objetivo de buscar as médias atualizadas de drops no nosso repositório do GitHub. Nenhum dado do usuário ou do computador é coletado ou transmitido.

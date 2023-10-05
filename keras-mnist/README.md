# Keras e MNIST
Criação, treinamento e aplicação de modelos para classificação de imagens no famoso dataset MNIST

A base de dados MNIST é uma grande coleção de algarismos manuscritos, frequentemente utilizada para treinar sistemas de processamento de imagens. Também é amplamente considerada para treinamento e teste no campo de aprendizagem de máquina. O conjunto conta com 60 mil imagens de treinamento e 10 mil imagens de teste. Todas as imagens possuem um tamanho de 28x28 pixels, com a cor do dígito branca em um fundo preto. Em 2017, surgiu o conjunto conhecido como EMNIST, uma versão expandida do original com 4x mais imagens: 240 mil para treinamento e 40 mil para teste.

Apesar de ser muito utilizada por pessoas em fase de evolução na área de Machine Learning e processamento de imagens, também é motivo de pesquisas profissionais, com pesquisadores testando modelos cada vez mais complexos. A intenção, obviamente, é desenvolver uma expertise nesse ramo para futuramente aplicar o conhecimento em outras ocasiões. O modelo mais preciso para esse dataset em específico foi revelado em 2020, na China, e atingiu uma eficácia de 99,91%. A lista completa de modelos, classificadores e taxas de erro está disponível [na página do MNIST na Wikipedia](https://en.wikipedia.org/wiki/MNIST_database#Classifiers) (em inglês). É interessante notar que, dos oito modelos mais eficazes, sete consistem em redes neurais convolucionais. Por esse motivo, esse tipo de modelo foi abordado nesse teste.

Esse repositório conta com dois arquivos, sendo um para modelos convencionais e um para modelos convolucionais. Como já era de se esperar, pelas informações do parágrafo acima, os modelos convolucionais atingem uma precisão muito maior. Ao longo de todo o desenvolvimento do projeto, foram criados 9 modelos.

---

**Ranking de desempenho dos modelos convolucionais**
* Relu - 99,23%
* Softplus - 99,00%
* Softsign - 98,82%
* Selu - 98,70%


**Ranking de desempenho dos modelos**
* Relu - 97,67%
* Softplus - 97,50%
* Softsign - 97,48%
* Selu - 97,34%
* Sigmoid - 95,82%

Dentre os 9 modelos criados, a maior eficácia apareceu no modelo convolucional com ativação **relu**, que atingiu uma taxa de erro de 0,77%. Esse valor colocaria o modelo como o 13º mais preciso na lista da Wikipedia, mas ainda configura um resultado muito interessante tendo em vista o tempo despendido na análise.

# Keras and MNIST
Creation, training, and application of models for image classification on the famous MNIST dataset

The MNIST dataset is a large collection of handwritten digits, often used to train image processing systems. It is also widely considered for training and testing in the field of machine learning. The dataset consists of 60,000 training images and 10,000 test images. All images are 28x28 pixels in size, with the digit's color being white on a black background. In 2017, the EMNIST dataset emerged, an expanded version of the original with 4 times more images: 240,000 for training and 40,000 for testing.

Although it is commonly used by people evolving in the field of machine learning and image processing, it is also the subject of professional research, with researchers testing increasingly complex models. The intention, of course, is to develop expertise in this area to apply the knowledge in other scenarios. The most accurate model for this specific dataset was revealed in 2020 in China, achieving an accuracy of 99.91%. The complete list of models, classifiers, and error rates is available [on the MNIST Wikipedia page](https://en.wikipedia.org/wiki/MNIST_database#Classifiers). It is interesting to note that of the eight most effective models, seven are convolutional neural networks. For this reason, this type of model was addressed in this test.

This repository contains two files, one for conventional models and one for convolutional models. As expected from the information in the paragraph above, convolutional models achieve much higher accuracy. Throughout the entire project development, nine models were created.

Performance ranking of convolutional models
* Relu - 99.23%
* Softplus - 99.00%
* Softsign - 98.82%
* Selu - 98.70%

Performance ranking of conventional models
* relu - 97.67%
* softplus - 97.50%
* softsign - 97.48%
* selu - 97.34%
* sigmoid - 95.82%
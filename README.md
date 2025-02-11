# IRC Malicous Communication Detection
Internet of Things (IoT) is growing every day, and its vulnerability, together with an increasing number of malicious attacks, represents a severe threat. The range of used protocols for communication is extensive, and one of them is Internet Relay Chat (IRC). IRC facilitates communication in the form of text and is designed for group communication in channels. This opens up the space for botnets that can be controlled by the master via an IRC channel.

In our research, we proposed a technique for detecting malicious communication in IRC. 
We took sniff traffic, and we extracted the IRC communication from the traffic. Since the IRC uses TCP, we separated the extracted IRC communication into TCP sessions. For each session, we extracted a set of features. The feature selection was made manually to provide a good means of characterizing malicious communication.

We took the extracted features that represent each session, and we analysed them by using several machine learning algorithms. Even with a small amount of data, we were able to create a model that achieved an accuracy 97.1% using the unsupervised learning and perfect accuracy 100.0 % using supervised learning. 

Data visualization confirmed us a suitable characterization of sessions since all the malicious sessions were projected closely to one position.




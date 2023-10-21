# SE364-Assignment2
SOFTENG 306 assignment 2 aims to write a Python-based chat program that supports communication among multiple clients based on one server and imposed encryption. Throughout the demo, it is recommended to establish one server and two clients whose names can be customized provided by the login system. The symmetric cryptography method implemented is AES, which facilitates the encryption progress and enhances security. The communication authorization is also assured by the built-in certificate that can be leveraged during the communication.

# Program setup
After cloning (downloading) the project, make sure the directory is set to the correct folder to enable the communication establishment

Initialize server:
```
python server.py --port=9988
```

Initialize clients:
```
python client.py --port=9988
```

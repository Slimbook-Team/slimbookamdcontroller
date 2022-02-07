# Slimbook AMD Controller

Slimbook AMD Controller works by setting your CPU TDP value. That is, the amount of power measured in watts that you CPU is allowed to draw to save battery or to improve the overall performance under heavy workloads like rendering jobs or serious number crunching on large spreadsheets. Increasing the TDP allows the CPU to use its boost frequency more often or even permanently on some scenarios.

Use this software with caution as the heat output will increase dramatically on the higher performance settings, we can't guarantee that all AMD CPU's will behave the same way, so your mileage may vary.

Slimbook AMD Controller is designed with mobile AMD Ryzen processors in mind. 

<br>

# Install
```bat
   sudo add-apt-repository ppa:slimbook/slimbook
   sudo apt install slimbookamdcontroller
```

![Testing version (Fixing Debian Issue)](https://github.com/slimbook/slimbookamdcontroller/releases/tag/Test)

![amdcontroller_0 3 2beta](https://user-images.githubusercontent.com/18195266/131973024-1cb2477a-82a2-4b6b-9910-90cbbd75baa7.png)
![amdcontrollergraph_0 3 2beta](https://user-images.githubusercontent.com/18195266/131973015-64ebd286-0ab7-4a7b-8bfa-e1239a847d18.png)

<br>

## Custom TDP setting:

This window allows you to set different TDP values for every mode. Default values are based in processor's line suffix and some motherboard TDP settings, to set this values by yourself, look up information about your processor's TDP, or take your motherboard TDP settings for your processor (plugged and unplugged), as a reference.

To check this out use:   
      
      sudo /usr/share/slimbookamdcontroller/ryzenadj --info

![Captura de pantalla de 2021-11-16 15-24-22](https://user-images.githubusercontent.com/18195266/142014508-0921d507-8fcb-4d3e-a438-df87daa7c854.png)

# Collaborate
   [**See 'To do' list**](https://github.com/slimbook/slimbookamdcontroller/projects/1)

<br>


Here you have link to the app tutorial!
--
[**Slimbook AMD Controller Tutorial**](https://slimbook.es/en/tutoriales/aplicaciones-slimbook/494-slimbook-amd-controller-en)

![amdcontrollerinfo_0 3 2beta](https://user-images.githubusercontent.com/18195266/131973146-cb0656d9-74f7-4dea-aaa3-2aaa196b42b3.png)


<br>
This software is protected with the GPLv3 license, which allows you to modify it with the same license and authorship. 

Thank you.

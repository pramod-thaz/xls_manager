# Wrapping svelte+flask+auth0 with flaskwebgui

Tested on python 3.9

## Installation

### Svelte

```bash
    $cd svelte-cleopatra
    $npm install
```

### flask

```bash
    $cd flaskwebgui
    $pip install -r requirements.txt
    $pip install pyinstaller
```

## Build svelte for flask

to build the svelte app for flask you need to do the following

1. make sure the folder `svelte-cleopatra`and `flaskwebgui` are besides each other
2. inside the svelte project run `$npm run build:app` , this will build the files inside flask


## Setting up Auth0

You need to setup Auth0 account (for now you can use my account to test the app)

1. login to auth0
2. go to `Applications` section, select the app, then insert the follwing allowed urls
![igm](https://i.ibb.co/6ntpysv/Auth0-config.png)

3. Get the authentication tokens and update the file `flaskwebgui/config.py`


The authentication will include google by default, to add linkedin you need to create linkedin app, just follow the [instructions of Auth0](https://auth0.com/docs/connections/social/linkedin)

## Run svelte with flask in dev mode

To run the project in dev mode, you can do

```bash
    $cd svelte-cleopatra
    $npm run dev
    $cd flaskwebgui
    $python main.py # this will run the API + the flaskwebgui
```
> PS: To avoid having the server closed when closing the tab, just comment the `new WebSocket("ws://127.0.0.1:5003/")` inside `index.html`, then uncomment it before the build



## Create exe file

To create exe you need to run 

```bash
 $cd flaskwebgui
 $python -m PyInstaller -w -F --onefile --add-data 'templates;templates' --add-data 'static;static' --add-data 'data;data' main.py


 alt for signing etc
  python -m PyInstaller -F --onefile --add-data "templates;templates" --add-data "static;static" main.py

 "C:\Program Files (x86)\Windows Kits\10\bin\10.0.19041.0\x64\signtool" sign /a dist\rv.exe
https://stackoverflow.com/questions/252226/signing-a-windows-exe-file

PowerShell
$cert = New-SelfSignedCertificate -DnsName www.realvectors.com -Type CodeSigning -CertStoreLocation Cert:\CurrentUser\My
$CertPassword = ConvertTo-SecureString -String "{sam007}" -Force -AsPlainText
Export-PfxCertificate -Cert "cert:\CurrentUser\My\$($cert.Thumbprint)" -FilePath "RV.pfx" -Password $CertPassword

 "C:\Program Files (x86)\Windows Kits\10\bin\10.0.19041.0\x64\signtool" sign /t http://timestamp.digicert.com  /F RV.pfx /P "{sam007}" /a dist\rv.exe


```
Export exe with console to debug

```bash
 $python -m PyInstaller --onefile --add-data 'templates;templates' --add-data 'static;static' --add-data 'data;data' main.py
```

this will generate `flaskwebgui/dist/main.exe` file

To see more options on how to change the icon you can add `--icon=app.ico` to command above or add it to spec file.

> PS: Make sure you put all your data files (non python) inside `flaskwebgui/data` 

### Use data from data folder
Don't use direct paths, they won't work when you build .exe , i've created the file `flaskwebgui/path_resolver.py` that has `resove` method to check the app environment.

```py
    from path_resolver import resolve
    path = resolve('data/yourfile.xlsx')
```

## Issues

### Terminating the flask app when closing the ui

The issue still exist
https://github.com/ClimenteA/flaskwebgui/issues/2

I Managed to get around this problem by running the flaskwebgui inside a process and use a websocket listener, as soon as the socket closes (user closes the window) it will terminate the process.

There is use case that still not working, it's when the user decides to quit before login, that's because the page exist is from auth0 and doesn't have websocket connection.


## Adding custom services

Inside the folder `flaskwebgui/services` create a package and add the code, you can see the example of blueprint `xlsx`.
Then import it inside `main.py`


## Caching problem
flaskwebgui (browser) caches the exported `static/build/bundle.js` file , to update the app for now (after first launch), you need to change the name (exp: `bundle2.js`) and use it in `templates/index.html`

> Maybe we can use some hash extention for rollup next time to separate the build versions https://github.com/sveltejs/template/issues/39
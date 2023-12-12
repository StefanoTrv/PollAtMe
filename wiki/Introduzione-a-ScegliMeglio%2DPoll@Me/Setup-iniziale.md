Di seguito si presentano le istruzioni per iniziare a lavorare al progetto:

## Prerequisiti

1.  Per utilizzare l'ambiente [devcontainer][devcontainer] installare
    
    - Visual Studio Code

    - Docker

    - L'estensione [Dev Containers][marketplace]

2. Copiare il file [.devcontainer/.env.default]() in [.devcontainer/.env]() e impostare le variabili d'ambiente

3. Premere Shift + Ctrl + P e digitare il comando
```
Dev Containers: Reopen in Container
```

4. Attendere il completamento della procedura di inizializzazione

5. Enjoy

### Eventuali problemi con git

#### git@ssh.dev.azure.com: Permission denied (password,publickey)
L'agente SSH non è configurato oppure la chiave SSH per Azure DevOps non è stata aggiunta all'agente.
La soluzione è [qui](https://code.visualstudio.com/docs/remote/troubleshooting#_setting-up-the-ssh-agent)

#### git detected dubious ownership
Esegui questo comando su un terminale (Powershell\Bash) dell'**Host**
```
git config --global --add safe.directory *
```
e riavvia VS Code

[devcontainer]: https://containers.dev/
[marketplace]: https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers



##Google authentication
Per sfruttare la funzionalità di autenticazione con google basta seguire la seguente guida al punto 4: https://dev.to/mdrhmn/django-google-authentication-using-django-allauth-18f8

Per le credenziali necessarie è necessario contattare i membri del team
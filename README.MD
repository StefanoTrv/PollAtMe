# Poll@Me
## Sistema online per le scelte sociali

Si richiede di costruire una web app che permetta di definire sondaggi a scelta multipla e raccogliere le
preferenze dei votanti.
Il sistema deve permettere di registrarsi e di avere uno spazio personale in cui gestire i sondaggi. I
sondaggi devono poter essere creati, avviati, chiusi, cancellati. I risultati devono poter essere visualizzati
e scaricati in formato csv.
L’interfaccia deve essere responsive.
Il sistema deve permettere ai votanti dei sondaggi di poter esprimere le proprie preferenze accedendo
tramite link o codice. I votanti devono avere la possibilità di accedere ad un’area riservata in cui poter
trovare tutti i sondaggi a cui possono partecipare e quelli a cui hanno partecipato.
I sondaggi devono poter essere di 3 tipi:

- A preferenza singola. In questo caso il votante deve poter scegliere solo una delle opzioni.
L’ordine finale delle opzioni è dato dalla somma delle singole preferenze.

- Metodo Schulze. Il votante deve poter ordinare le opzioni. L’ordinamento non è necessariamente
stretto e quindi più opzioni possono ottenere lo stesso ordine. Ad esempio, se le opzioni sono $A, B, C, D$, con il metodo Schulze un votante può ordinare $C > B > A > D$ che significa che preferisce
tra tutte l’opzione $C$ e poi, come seconda scelta $B$, come terza $A$ e infine $D$, oppure $B > A = D > C$, che significa che la sua prima scelta è $B$, come seconda è indifferente tra $A$ e $D$, ma che comunque le preferisce entrambe a $C$.
L’ordine finale delle opzioni è dato dal seguente algoritmo:

  1. Si costruisce un grafo orientato in cui i nodi sono le opzioni e gli archi sono pesati. Esiste un arco di perso $p$ tra i nodi $N$ e $M$ se $N$ compare prima di $M$ in esattamente $p$ ordinamenti espressi dai votanti al sondaggio e $M$ compare prima di $N$ in un numero di volte $q < p$.

  2. Se il grafo è aciclico, allora rappresenta l’ordinamento delle opzioni.

  3. Se esiste almeno un ciclo, allora va eliminato girando uno degli archi. L’arco del ciclo che va invertito è l’arco $N \to M$ con peso $p$ per cui lungo il cammino $M \Rightarrow N$ tutti i pesi sugli archi sono maggiori di $p$. In questo caso si sostituisce $N \to M$ con $M \to N$ con peso uguale al minimo peso lungo il cammino.

- Metodo del giudizio maggioritario. Il votante esprime un giudizio su una scala a 5 o 7 valori che vanno da Ottimo a Pessimo, per ognuna delle opzioni. L’ordinamento finale è dato dal calcolo del giudizio maggioritario secondo il seguente algoritmo:

    1. Si calcola il grado maggioritario di ogni opzione che è dato dal peggiore dei valori mediani.

    2. Aggiungo un segno + se il numero di votanti che hanno espresso un giudizio strettamente migliore sono più di coloro che hanno espresso un giudizio strettamente peggiore del grado maggioritario.

    3. Scrivo una tripla data da <#giudizi migliori, grado maggioritario con segno, #giudizi peggiori>

    4. Le opzioni vengono ordinate secondo il grado maggioritario

        a) A parità di grado, il segno + prevale su -

        b) A parità di segno + prevale l’opzione con un numero di giudizi migliori superiore

        c) A parità di segno - prevale l’opzione con un numero di giudizi peggiori inferiore

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

## Eventuali problemi con git

### git@ssh.dev.azure.com: Permission denied (password,publickey)
L'agente SSH non è configurato oppure la chiave SSH per Azure DevOps non è stata aggiunta all'agente.
La soluzione è [qui](https://code.visualstudio.com/docs/remote/troubleshooting#_setting-up-the-ssh-agent)

### git detected dubious ownership
Esegui questo comando su un terminale (Powershell\Bash) dell'**Host**
```
git config --global --add safe.directory *
```
e riavvia VS Code

[devcontainer]: https://containers.dev/
[marketplace]: https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers
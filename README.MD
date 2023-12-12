# Poll@Me
## Importante
Questo progetto è stato sviluppato con Azure DevOps. Il seguente readme è composto da tutti i file di documentazioni presenti nella repository originale. I testi si riferiscono all'ambiente di sviluppo originale, quindi potrebbero risultare fuori contesto in questa repository copia.

# ReadMe
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




# Introduzione
In questa pagina verranno brevemente spiegate le informazioni necessarie per poter iniziare a lavorare in questo progetto. Si assume che il lettore abbia una conoscenza minima del framework di lavoro **Scrum**, dal momento che verranno dati per scontati alcuni termini/concetti tipici di tale strumento.

# Il team
- Nome del team: **HeavyWare**
- Membri: Riccardo Belliato, Stefano Travasci, Simone Tomada, Riccardo Zamolo Diletta Giabardo 
- Nome in codice del prodotto: **Poll@Me (PollAtMe)**
- Nome del prodotto: **ScegliMeglio**

# Informazioni generali
La repository del progetto si trova su Azure: [https://dev.azure.com/ingsw2223-heavyware/_git/PollAtMe].
I task e le storie da sviluppare si trovano sempre su Azure nella sezione Boards.

Per questioni di uniformità degli strumenti di lavoro tra i membri del team, si è stabilito di utilizzare docker per sviluppare il progetto. Informazioni più tecniche si possono reperire nelle sotto-pagine, a partire dalla configurazione iniziale del container docker. Si consiglia caldamente la lettura ordinata delle sotto-pagine.

## Strumenti di comunicazione del team
- _Microsoft Teams_, in cui si richiede di inserire nel calendario del team i propri impegni, in modo che lo scrum master possa schedulare i daily standup in maniera agevole
- _Telegram_, come app di messaggistica a supporto di Teams (esiste una chat di gruppo).




# Setup Iniziale
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

##Google authentication
Per sfruttare la funzionalità di autenticazione con google basta seguire la seguente guida al punto 4: https://dev.to/mdrhmn/django-google-authentication-using-django-allauth-18f8

Per le credenziali necessarie è necessario contattare i membri del team




# Politiche di gestione del versionamento e pipeline

## Versionamento
Per quanto riguarda il versionamento del codice, si è deciso di attenersi a quanto imparato a lezione, utilizzando git. Pertanto, uno schema di massima, relativo alla gestione dei branch è il seguente:

![versionamento.svg](/.attachments/versionamento-f261054b-b110-4941-9db7-eee7764df2fb.svg)

All'inizio dello sprint n, ci si ritrova con i branch _master_ e _dev_ sincronizzati con l'ultima release dello sprint n-1. La differenza tra i due branch stà nel fatto che il branch _master_ viene aggiornato solamente in fase di release. Alla fine di ogni sprint viene fatta una nuova release; possono essere fatte delle release durante lo sprint se lo si ritiene necessario o opportuno. Il branch _dev_ invece viene tipicamente aggiornato ogniqualvolta una feature (user story) viene completata. 

Per sviluppare una feature o una sottoparte consistente di una feature si crea un nuovo branch a partire da _dev_, in modo da evitare che diversi sviluppatori si sovrappongano lavorando contemporaneamente sullo stesso branch. Per convenzione, il nome dei branch relativi a nuove funzionalità (o parti di esse) iniziano con _"feature/"_ e quelli dei branch relativi a fix _"fix/"_.  Nell'esempio sopra si vede come i due branch _feature/share_ e _feature/random_options_ hanno origine da _dev_ e, una volta terminato il lavoro, vengono fusi nuovamente in _dev_.

Come si può notare in figura, al branch _master_ è associato il [sito di produzione](https://sceglimeglio.azurewebsites.net/), mentre al branch _dev_ è associato il [sito di pre-produzione](https://sceglimeglio-dev.azurewebsites.net), utile per provare le feature sviluppate prima di effettuare la release in _master_.

## Pull request
Il meccanismo di approvazione delle modifiche (ovvero il merge dei branch) è quello tipico di git, ovvero le pull requests.
Le pull request possono essere approvate solo se tutti i test automatizzati eseguiti dalla pipeline sono privi di errori. Inoltre devono essere collegati alla pull request i backlog item e/o i task che sono stati completati; questo non è strettamente obbligatorio nei casi in cui non sia stato inserito nel backlog o nella taskboard un item correlato (in generale però questo non dovrebbe accadere).
È compito del product owner controllare ed approvare le **pull request in _dev_**: deve verificare che gli obiettivi del branch (quindi una nuova feature o una sua parte) siano stati raggiunti e che non ci sia stata un regressione della qualità del prodotto. Particolare attenzione va prestata ai criteri di accettazione e ai test automatizzati: in generale, una pull request dovrebbe sempre contenere nuovi test automatizzati che controllino le nuove feature o modifiche (quando queste cose sono testabili, si veda [Testing](/Introduzione-a-ScegliMeglio%2DPoll@Me/Testing) per maggiori dettagli). È importante che, al momento della creazione di una pull request in _dev_, il product owner venga selezionato come required reviewer.
Le **pull request in _master_** devono invece essere approvate da tutti i membri del team. Non è necessario che il product owner faccia gli stessi controlli richiesti per le pull request in _dev_, in quanto si suppone che siano stati già fatti, ma ha il compito di assicurarsi che la release sia stata rilasciata con successo e di verificare ulteriormente il corretto funzionamento del sistema in produzione.

**Si veda anche la [definizione di done](/Definizione-di-Done).**

Per questioni di sicurezza, i commit di modifiche direttamente verso i branch _dev_ e _master_ sono bloccati.

## Migrazioni del database
Nel caso un merge includesse delle migrazioni, queste vengono applicate automaticamente sia in _dev_ che in _master_.

## Pipeline CI/CD
Ogni volta che viene effettuato un nuovo commit, la pipeline effettua automaticamente i test automatizzati e altri controlli (come il code coverage) sui branch remoti che hanno il prefisso "_feature/_" o "_fix/_" e sui due branch remoti principali _dev_ e _master_. È comunque buona norma far girare i test in locale prima di fare un push sui branch remoti.
La pipeline non verrà eseguita per tutti gli altri branch, quindi è fortemente sconsigliato create branch che non abbiano "_feature/_" o "_fix/_" come prefisso.




# Architettura

Il progetto è sviluppato con il framework Django. Questo significa che ci atteniamo all'architettura Django MVT (Model-View-Template), con aggiunto un layer di servizi, di seguito è mostrato uno schema ad alto livello dell'architettura.

![ModelloArchitettra.drawio (2).svg](/.attachments/ModelloArchitettra.drawio%20(2)-30e0ddc6-da34-4422-a98f-a83848b1a900.svg)

- ### Model
  Il database (in data 5/6/2023) utilizza il seguente modello, implementato tramite i Model di Django:

![ModelloDatabase3.svg](/.attachments/ModelloDatabase3-c1636dc5-e53c-4894-acf0-fddd25d8ec2b.svg)

- ### View
  Le View di Django si occupano di recuperare e preparare i dati da rendere disponibili ai template, con l'eventuale supporto di servizi e/o form. Possono comunicare con il database nel caso di query non eccessivamente complesse da giustificare l'esistenza di un servizio.

- ### Services/Forms
  Al fine di separare la logica di business dalle Views, è stato inserito un layer relativo ai servizi e ai form in cui sono contenuti principalmente query al database, algoritmi, ecc. I servizi potrebbero eventualmente se utile esposti all'esterno mediante delle API Rest.

- ### Template
  Per il front-end del progetto utilizziamo i template di Django, insieme a bootstrap e javascript. In particolare, ci si ispira al [template Django Gradient Able](https://django-gradient-able.appseed-srv1.com/).

Il database usato da Django è PostgreSQL.

Nell'applicazione, utilizziamo i seguenti componenti di terze parti:
- [whitenoise.runserver_nostatic](https://whitenoise.readthedocs.io/en/latest/) per la gestione dei file statici
- [django-cookiebanner](https://pypi.org/project/django-cookiebanner/) per il banner dei cookies
- [django_bootstrap5](https://django-bootstrap5.readthedocs.io/en/latest/) per integrare bootstrap in Django
- [bootstrap_datepicker_plus](https://pypi.org/project/django-bootstrap-datepicker-plus/) per il datepicker utilizzato nei form
- [allauth](https://django-allauth.readthedocs.io/en/latest/) (in varie sotto-applicazioni) per il login con Google. `justsocialauth.apps.JustSocialAuthConfig` è una versione che abbiamo modificato per includere solo il login con Google.
- [django-qr-code](https://pypi.org/project/django-qr-code/) per gestire i codici qr




# Testing

Quando si sviluppa una nuova feature, è necessario scrivere dei test automatizzati che controllino che essa funzioni come ci si aspetta, sia nelle situazioni standard che in quelle di errore. Le User story principali devo disporre di una descrizione più o meno dettagliata dei test che devono essere sviluppati. Al momento non è possibile creare test automatizzati per testare le interazioni dell'utente con il front end (javascript, aspetto grafico, ecc.).

Come detto in [Politiche di gestione del versionamento e pipeline](/Introduzione-a-ScegliMeglio%2DPoll@Me/Politiche-di-gestione-del-versionamento-e-pipeline), le pull request possono essere approvate solo se tutti i test automatizzati eseguiti dalla pipeline sono privi di errori e se ci sono test adeguati per controllare il funzionamento corretto delle nuove features o modifiche, quando questi test sono realizzabili.

Per realizzare i test usiamo _unittest_, in particolare usiamo la sottoclasse `django.test.TestCase` di `unittest.TestCase`, che è specifica di Django. Per realizzare le asserzioni usiamo invece il metodo `assert_that()` di _assertpy_. Fanno eccezione i test che coinvolgono le response HTML, per cui usiamo le funzioni di asserzione definite da `django.test.TestCase`.

## Linee guida sui test
Nello sviluppo dei test, si cerchi di seguire queste linee guida:
- **Test completi:** i test devono testare a fondo che ciò che stà esaminando funzioni correttamente, non solo in modo superficiale. Ad esempio, se vogliamo controllare che un voto venga salvato correttamente, non ci limitiamo a controllare che l'utente venga reindirizzato ad una pagina di conferma del voto avvenuto, ma controlliamo anche che il voto sia stato salvato in modo corretto nel database.
- **Test di funzionamento nelle situazioni normali:** si deve testare che la feature funzioni correttamente nelle circostanze normali di utilizzo.
- **Test dei casi di errore:** devono essere testati tutti i tipi di casi di errore a cui una feature può andare incontro. È necessario testare che l'errore venga rilevato (ovvero che l'esecuzione non prosegua come se non fosse in una situazione di errore), che l'errore venga gestito correttamente (cioè che l'errore non si propaghi nei dati o nel processo) e che venga segnalato correttamente (ad esempio, visualizzando la corretta pagina di errore); tutto ciò dovrebbe essere fatto in un'unica funzione di test. Non è necessario testare le combinazioni di più errori in contemporanea, a meno che la situazioni specifica non lo renda opportuno.
- **Evitare dipendenza dalla presentazione:** evitare che i test dipendano dal modo specifico in cui vengono mostrati i risultati, ad esempio controllando che una pagina mostri un particolare testo. Per evitare ciò, è opportuno inserire nei template dei commenti HTML che contengano le informazioni che vogliamo verificare che siano presenti correttamente nella pagina, in modo che i test vadano a cercare il testo nei commenti creati apposta per loro invece che nel testo che viene mostrato all'utente, che potrebbe invece facilmente essere modificato.
- **Non usare le fixture:** usare la funzione di `setup` per riempire il database con gli oggetti necessari ai test, o crearli direttamente nel corpo della funzione di test in caso essa abbia bisogno di oggetti molto specifici. Alcuni vecchi test usano le fixture, ma per facilità di creazione e manutenzione dei test si è scelto di non usarle più.
- **Testare i form:** testare che i form, in particolare la loro validazione, funzionino in modo corretto. Anche qui, testare tutti i casi in cui la validazione può fallire.
- **Test dei bug:** quando è possibile, nel momento in cui si risolve un bug, aggiungere un test che verifichi la sua effettiva risoluzione.

## Falsi positivi e falsi negativi
Quando un test non funziona, perché si è verificato che dà luogo a falsi positivi o falsi negativi, è massima priorità correggerlo. Si ponga particolare attenzione nel capire se un falso negativo è effettivamente tale (ovvero il test non individua un errore che ha il compito di individuare) o se è invece necessario creare un nuovo test per verificare una nuova situazione di errore, perché l'errore che si vuole rilevare non rientra nello scopo del test originale.

## Inserimento di dati per i test manuali
A volte durante lo sviluppo di nuove feature può essere utile inserire manualmente dei dati nel database per verificare il funzionamento o il comportamento delle funzionalità.

Un modo possibile per fare ciò è il seguente:
1. Creare un super user attraverso il comando: "_python manage.py createsuperuser_" (l'email non è obbligatoria)
2. Nel file _admin_ presente nella cartella _Poll_ registrare i modelli desiderati attraverso il comando: _admin.site.register(modello_desiderato)_
3. Accedere alla pagina di _admin_ (ad esempio all'url "_localhost:8000/admin_")
4. Inserire i dati desiderati nelle tabelle registrate.

**Attenzione:** non pushare le modifiche al file admin.

Un modo alternativo è aprire la shell di Django con il comando "_python manage.py shell_", importare le classi dei modelli con "_from Polls.models import *" e quindi inserire i dati nelle tabelle usando codice python.




# Definizione di Done

Una user story (o un backlog item in generale) è "done" quando si verificano tutte queste condizioni:
1. è stata implementata;
1. sono stati aggiunti nuovi test automatizzati che la testano;
1. tutti i test (nuovi e preesistenti) vengono superati;
1. è stata aperta una pull request sul branch dev a cui sono stati collegati correttamente i work items corrispondenti;
1. la pipeline di continuous integration viene completata senza errori;
1. il Product Owner ha approvato l'incremento di funzionalità (e quindi la pull request);
1. la pull request viene completata senza errori.






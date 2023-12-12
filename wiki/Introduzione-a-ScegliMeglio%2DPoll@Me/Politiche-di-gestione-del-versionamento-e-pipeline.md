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


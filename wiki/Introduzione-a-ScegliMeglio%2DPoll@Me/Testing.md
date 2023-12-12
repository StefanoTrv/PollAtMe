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
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


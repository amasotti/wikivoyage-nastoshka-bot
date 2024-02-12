# Installazione e uso degli script `pywikibot`

## Introduzione

Pywikibot è - tra i tool e framework disponibili - uno dei più potenti e flessibili per l'automazione di operazioni sui progetti Wikimedia
e in generale sui progetti che usano il software [MediaWiki](https://www.mediawiki.org/).

Questa guida è scritta per aiutare chiunque voglia iniziare a usare pywikibot per automatizzare operazioni. Conoscenze di
base di Python (come avviare uno script, come installare un modulo) sono necessarie, ma a meno che non si voglia scrivere
script complessi, non è necessario conoscere a fondo il linguaggio.

Per iniziare c'è bisogno di pochi *ingredienti*:

### Gli ingredienti


* **Python** (3.7 o successive): è il linguaggio di programmazione su cui pywikibot è basato, ed uno dei più diffusi al mondo, con una 
    vasta comunità di sviluppatori e un'ampia documentazione basata sui più di 30 anni di storia del linguaggio. Python è facilissimo da
    imparare e da usare (basta una settimana per imparare le basi), ed è molto potente e flessibile, senza l'overhead di linguaggi più
    complessi come Java o C++. D'altro canto, a differenza dei linguaggi utilizzati per il web (PHP, Nodejs, Ruby, ecc.) per cui basta 
    un browser e un editor di testo, Python richiede un'installazione sul proprio computer. L'installazione è molto semplice, e vi regalerà
    due tools molto utili: 
    * l' **interprete** Python, che permette di eseguire script direttamente da riga di comando (Powershell, CMD, Bash, ecc.)
    * il **package manager** `pip`, che permette di installare e gestire i moduli Python (chiamati anche *pacchetti* o *librerie*) nel caso vi servano 
    moduli aggiuntivi a quelli già installati con Python.
* **pywikibot** (versione 8.6 o successive): è il modulo Python che permette di interagire con i progetti Wikimedia. Permette di fare praticamente tutto quello 
    che si può fare manualmente, ma in modo automatico (creare, avvisare e bloccare utenti, categorizzare pagine, estrarre templates, creare, modificare, proteggere o cancellare pagine ecc.). 
    Arrivato alla versione 8.6 (con la v.9 già in sviluppo), pywikibot è un modulo molto complesso, e la sua documentazione è molto vasta e complessa, ma per iniziare a usarlo non è necessario
    conoscere tutto. In sostanza quello che pywikibot porta con se è una serie di classi, metodi e pratiche funzioni per interagire con ogni aspetto di un progetto Wikimedia. Sono
    anche disponibili una serie di script già pronti per fare operazioni comuni, e che possono essere usati come base per script più complessi.
    Il motivo per cui è molto amato risiede nel fatto che è incredibilmente facile da estendere e personalizzare.
* **git** (opzionale) Per utilizzare gli scripts in questo repository e magari modificarli è consigliato utilizzare un VCS (*version control system*). Git è un sistema di controllo versione distribuito, 
    che permette di tenere traccia delle modifiche ai file, e di collaborare con altri sviluppatori. Anche se non si è sviluppatori, git è molto utile per scaricare e aggiornare i file 
    di questo repository, e per tenere traccia delle modifiche che si fanno ai file. Se non si intende modificare gli script, o modificarli solo per se stessi, senza condividerli con altri,
    git non è necessario. In ogni caso, è molto facile da installare e usare, e ci sono molti tutorial e guide in rete.
* **custom scripts**: Una volta installati Python e Pywikibot, l'unica cosa che serve sono gli script in questo repository. Gli script sono scritti in Python, e possono essere eseguiti
    direttamente da riga di comando. Nella cartella [bot/wikivoyage/scripts](./bot/wikivoyage/scripts) ci sono una serie di file Markdown [come questo](./bot/wikivoyage/scripts/ItemlistWikidataCompleter.md) che spiegano
    come usare gli script.

### 1. Installazione di Python

Installare Python è davvero semplice: per gli utenti Linux e Mac, Python è già installato di default, e non c'è bisogno di fare nulla. 
Per gli utenti Windows, è necessario scaricare il file di installazione [dal sito ufficiale](https://www.python.org/) e seguire
le istruzioni. Durante l'installazione, è consigliato spuntare la casella "aggiungi Python al PATH", che permette di eseguire Python
da riga di comando senza dover specificare il percorso del file eseguibile.


**Nota (opzionale)**: Python diventa presto una specie di droga per chi lo usa, data la sua semplicità e ampio uso in tantissimi
campi (scripting, ma anche data analysis, intelligenza artificiale, web development, ecc.). Alcuni sistemi operativi
come Linux e Mac usano Python per alcune funzioni di sistema. Col tempo si rischia di aver bisogno di diverse 
versioni di Python e di moduli che potrebbero essere in conflitto tra loro. Per questo motivo, è consigliato, anzi
consigliatisssimo, usare un *ambiente virtuale* per ogni progetto. Un ambiente virtuale è una specie di sandbox
in cui si può installare una versione specifica di Python e i moduli necessari per un progetto, senza che questi entrino in conflitto con
quelli di altri progetti. 

Nel mondo Python ci sono diversi modi per creare e gestire ambienti virtuali:

* `venv` è un modulo di Python che permette di creare e gestire ambienti virtuali. È incluso in Python 3.3 e successive, e permette di creare ambienti virtuali in pochi secondi.
con il comando `python -m venv nome_ambiente` si crea un ambiente virtuale, e con `nome_ambiente\Scripts\activate` si attiva. Per disattivarlo, basta digitare `deactivate`.

* [Conda](https://docs.conda.io/projects/conda/en/stable/) è un gestore di pacchetti e ambienti virtuali molto potente e flessibile, che permette di creare ambienti virtuali 
   con diverse versioni di Python e di moduli, e di gestirli in modo molto flessibile. È molto utile per chi fa data analysis, ma è molto utile anche per chi fa sviluppo web o 
   scripting. Conda è un progetto open source, e ha una vasta comunità di sviluppatori e utenti, e una vasta documentazione.

* [Mamba](https://mamba.readthedocs.io/en/latest/) è la versione in C++ di Conda, e permette di creare e gestire ambienti virtuali in modo molto più veloce di Conda. 
   Mamba è molto utile per chi ha bisogno di creare e gestire molti ambienti virtuali, e per chi ha bisogno di velocizzare l'installazione di moduli e ambienti virtuali.

### Installazione e configurazuione di pywikibot

Una volta installato Python, è possibile installare pywikibot con il comando `pip install pywikibot`. Questo comando scaricherà e installerà
pywikibot e tutti i moduli di cui ha bisogno. Se state utilizzando un ambiente virtuale, è consigliato installare pywikibot in un ambiente virtuale (vedi sopra).
La documentazione ufficiale è [disponibile qui](https://www.mediawiki.org/wiki/Manual:Pywikibot/Installation#Shortcut_in_command_line) (scegli "On your own computer"). 

La [Guida](https://www.mediawiki.org/wiki/Manual:Pywikibot/Installation#Install_Pywikibot) spiega passo per passo come installarlo. Oltre
a pywikibot stesso, è necessario installare anche i moduli `mwparserfromhell` e `wikitextparser`:

```sh
pip install pywikibot # installa pywikibot
pip install mwparserfromhell # installa mwparserfromhell, il parser di codice wiki
pip install requests # installa requests, un modulo per fare richieste HTTP
pip install packaging # installa packaging, un modulo per gestire i pacchetti
```

Una volta installato, verifica che sia installato correttamente con il comando `pwb --version`. Se tutto è andato bene, dovresti vedere qualcosa di simile a questo output:

```
Pywikibot: pywikibot/__init__.py (, -1 (unknown), 2024/01/13, 21:25:03, UNKNOWN)
Release version: 8.6.0
setuptools version: 68.0.0
mwparserfromhell version: 0.6.6
wikitextparser version: 0.55.7
```


Una volta installato è necessario configurarlo. Per farlo, basta eseguire il comando `python pwb.py generate_user_files` e seguire le istruzioni.
Pywikibot ti porrà una serie di domande (nome utente, password, lingua, progetto wikimedia ecc.), e creerà un file di configurazione chiamato
`user-config.py` simile al seguente:

```py 
# This is an automatically generated file. You can find more
# configuration parameters in 'config.py' file or refer
# https://doc.wikimedia.org/pywikibot/master/api_ref/pywikibot.config.html
from typing import Optional, Union

from pywikibot.backports import List
family = 'wikivoyage'
mylang = 'it'
usernames['wikivoyage']['it'] = 'ToshkaBot'
password_file = "user-password.py"
debug_log: List[str] = []
user_script_paths: List[str] = ["bot/wikivoyage/scripts", "bot/wikidata/scripts"]
```

Il file può essere modificato a piacere, e contiene tutte le impostazioni di pywikibot. In particolare, è possibile specificare
- il progetto Wikimedia (family)
- la lingua (mylang)
- il nome utente (usernames)
- il file di password (password_file): è consigliato creare una password separata con [Speciale:BotPasswords](https://it.wikivoyage.org/wiki/Speciale:BotPasswords) in modo da non avere la password usata per l'account principale in chiaro sul computer.
  Un altro vantaggio delle password Bot è che è possibile stabilire in maniera precisa quali permessi dare al bot, e di revocarli in qualsiasi momento.
- il percorso degli script (user_script_paths): dove si trovano gli scritti personalizzati, vedi punto seguente.

### 2. Esecuzione degli script

Uno dei parametri precedenti è il percorso degli script. Gli script sono file Python che possono essere eseguiti direttamente da riga di comando.
Dai un'occhiata alla cartella [bot/wikivoyage/scripts](./bot/wikivoyage/scripts) per vedere quali script sono disponibili in questo repository.

In generale per avviare uno script basta eseguire il comando `pwb <nome_script> <opzioni>` da riga di comando.
Le opzioni possono essere quelle [standard di pywikibot](https://doc.wikimedia.org/pywikibot/stable/global_options.html) o specifiche dello script.

Tra le opzioni standard ci sono ad esempio:

`-cat:NomeCategoria` - per processare tutti i file in una specifica categoria
`-simulate` - per eseguire lo script in modalità simulazione, senza fare modifiche
`-log` - per creare un log file con tutte le operazioni eseguite
e molte altre

Per le opzioni specifiche di uno script, consulta il file Markdown corrispondente. Vedi [CompleteWikidataItem](./bot/wikivoyage/scripts/ItemlistWikidataCompleter.md) per un esempio.


## Sum up

In sostanza, per poter eseguire gli script in questo repository, è necessario:

1. Avere Python sul proprio computer
2. Avere pywikibot installato (con i moduli ausiliari)
3. Avere un file di configurazione `user-config.py` con le impostazioni corrette
4. Avere gli script che si vogliono eseguire


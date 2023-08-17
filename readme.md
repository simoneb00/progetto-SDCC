# TODO
* Aggiungere randomicità alle città
* Implementare il meccanismo di cold start:
  * Container intermedio sempre attivo che mantiene "tabella" dei container attivi, si occupa del routing e, se un container che deve ricevere dati è inattivo, il dispatcher attiva il container e, nel frattempo, soddisfa la richiesta.
* Aggiungere meccanismo di spegnimento dei container
  * Se un container non riceve dati per due round consecutivi, viene spento (e.g. mantiene un timer di 2 minuti, al termine del quale, se non viene riavviato, si spegne. Il timer viene riavviato alla ricezione di nuovi dati)
* Invio dati al cloud
* Realizzazione funzioni in-cloud (serverless)
  * Salvataggio su storage (S3)
  * Altre cose da vedere (CloudWatch)
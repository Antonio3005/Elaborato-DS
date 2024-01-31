# Elaborato-DS  Antonio Inveninato - Angelo Cocuzza
__Build del docker compose__  
Per effettuare il build del progetto utilizzare il file docker-compose.yaml  
Una volta avviato docker engine, posizionarsi nella root directory del progetto e digitare nel terminale il seguente comando:  
docker compose up --build  
In questo modo verranno costruite le immagini dei microservizi a partire dai dockerfile definiti nelle diverse directory.  
Inoltre, verranno creati anche i volumi per le componenti del progetto (i database e prometheus) e la rete in cui si collocano i microservizi.  

Qualora, invece, si volesse effettuare il build del singolo microservizio, posizionarsi nella root specifica e digitare il seguente comando,  
specificando nome dell'immagine e tag:  
docker build -t <image_name>:<image_tag>


**Deploy su Kubernetes**   
Inanzitutto creare le immagini su Docker Hub ai fini di rendere disponibili globalmente i container, semplificando il deployment su Kubernetes:  
Apri un terminale e esegui il comando per effettuare il login su Docker Hub:  
docker login  
Inserisci le tue credenziali Docker Hub (username e password).  
Tagga l'immagine con il tuo username Docker Hub e il nome del repository. Supponiamo che tu stia lavorando con l'immagine app:latest   
e il tuo username Docker  Hub sia tuo_username.  
docker tag app:latest tuo_username/app:latest   
Ora carica l'immagine taggata sul tuo account Docker Hub:  
docker push tuo_username/app:latest   
Questo comando caricherà l'immagine sull'hub Docker.  
Ripeti questo passaggio per creare nel Docker Hub tutte le immagini dei microservizi:  
auth_service,api_service,sla_service,subscription_service,notifier_service.  

Per effettuare il deploy su Kubernetes in locale utilizzare Kind ed installare Kubectl:  
Posizionarsi all'interno della directory kubernetes e creare il cluster usando il seguente comando:  
kind create cluster --config=config-yml  
in questo modo verrà creato un cluster costituito da due nodi: un control plane node e
un worker node. Il cluster sarà raggiungibile tramite localhost, usando le porte 80 (HTTP) e 443 (HTTPS).  
Creato il cluster effettuare il deploy dei microservizi col seguente comando:  
kubectl apply -f __filename__.yml  
Nello specifico, l'ordine in cui fare il deploy è il seguente:  

NGINX - ingress.yml:  
effettuare prima il deploy del modulo NGINX col comando:  
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml  
e poi applicare il file di configurazione ingress.yml;  
DATABASE:  
effettuare il deploy dei database, in quanto i relativi microservizi, una volta avviati, proveranno subito a connettersi con essi. Se non ci fossero restituirebbero un errore;  
KAFKA:  
effetuare il deploy del broker Kafka in quanto essenziale alla comunicazione ; dopo aver deployato kafka, bisognerà creare i due topic, users e flights, utilizzati dai tre microservizi. Per fare ciò utilizzare il seguente comando, dove bisognerà specificare il nome del pod kafka e il nome del topic che si vuole creare:  
kubectl -n dsbd exec -it __kafka-pod-name__ -- /bin/bash -c "kafka-topics --bootstrap-server kafka:9092 --create --if-not-exists --topic __topic-name__ --replication-factor 1 --partitions 1"  
MICROSERVIZI:  
infine, sarà possibile effettuare il deploy di tutti i microservizi restanti sempre con lo stesso comando.  

**Client**   
Per comunicare con i microservizi sla_manager,auth_service,subscription_service sono stati creati dei file html all'interno dei quali vengono eseguite richieste agli endpoint dei microservizi sopracitati.  
Per effettuare queste richieste basta aprire i relativi file .html (contenuti nella directory templates) con un qualsiasi browser.

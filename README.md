# warsaw-ai-hackaton

## VisSegBud - opis budowy za pomocą sztucznej inteligencji

VisSegBud to program do opisywania i zaznaczania poszczególnych części danego obrazu budowy za pomocą segmentowania obrazu. Dostęp do tej funkcjonalności jest możliwy przez webowy interfejs użytkownika

# jak uruchomić backend
 
w `src/` `./run_backend.sh` i trzymać mocno kciuki, że będzie działać 

# jak uruchomić frontend

1. Przejdź do `src/ui`
2. Upewnij się, że na maszynie jest zainstallowany bun (https://bun.com/docs/installation)
3. Uruchom `bun install`
4. Uruchom `bun start`
5. Uruchom przeglądarkę z wyłączonym CORS'em (w przypadku uruchamiania chrome'a na Macu, uruchom `open -n -a /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --args --user-data-dir="/tmp/chrome_dev_test" --disable-web-security`)
6. Otwórz http://localhost:3000
# warsaw-ai-hackaton

## VisSegBud - opis budowy za pomocą sztucznej inteligencji

VisSegBud to program do opisywania i zaznaczania poszczególnych części danego obszaru budowy za pomocą segmentowania obrazu. Użytkownik, może zapytać bota o dowolną statystykę z placu budowy, która da się wyczytać z zdjęcia z lotu ptaka. Przykładowo jest w stanie policzyć liczbę aut budowlanych obecnych na placu, jest to przykład problemu, który ma rzeczywiste zastosowanie na placach budowy. Pod spodem używamy najnowszych modeli językowych od google, którym dodajemy możliwość przeprowadzania zero-shot detekcji oraz segmentacji zdjęcia placu budowy z lotu ptaka. Wykorzytujemy do tego najnowszy open-source model od Mata, SegmentAnything 3, osiągając bardzo satysfakcjonuje wyniki. 

# jak uruchomić backend
 
w `src/` `./run_backend.sh` i trzymać mocno kciuki, że będzie działać 

# jak uruchomić frontend

1. Przejdź do `src/ui`
2. Upewnij się, że na maszynie jest zainstallowany bun (https://bun.com/docs/installation)
3. Uruchom `bun install`
4. Uruchom `bun start`
5. Uruchom przeglądarkę z wyłączonym CORS'em (w przypadku uruchamiania chrome'a na Macu, uruchom `open -n -a /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --args --user-data-dir="/tmp/chrome_dev_test" --disable-web-security`)
6. Otwórz http://localhost:3000
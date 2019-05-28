# Semestrální práce

Semestrální práce na téma registrace obrazových dat CT snmků pomocí nátrojů ITK a SimpleITK

## SPC_Registration

Python skript, který sdružuje jednotlivé metody. Je možné po jeho spuštění definovat jaká bude použita metoda a metrika. Další možností je spuštění postupně všech implementovaných metod při zvolení jedné metriky. Tato varianta pak uloží výsledky porovnání jednotlivých metod
```
Give examples
```

## Obsah složek

* [Old_tests](http://www.dropwizard.io/1.0.2/docs/) - Staré původní testy převážně založené na 2D registraci obrazových dat. Využívají především nástroj ITK a jsou zde použity pokusy s vlastní metrikou.
* [Registration_Methods_Using_SITK](https://maven.apache.org/) - Testy s jednotlivými metodami pro registraci 3D obrazových dat. Jsou zde jednotlivě implementované registrační metody MutualInformation,B_Spline metody a metody využívající DemonsRegistrationFilter 
* [SimpleITK_Tests](https://rometools.github.io/rome/) - Dílčí testy
* [Results] (https://rometools.github.io/rome/)- příklady registrovaných 3D snímků

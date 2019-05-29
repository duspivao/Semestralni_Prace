# Semestrální práce

Semestrální práce na téma registrace obrazových dat CT snmků pomocí nátrojů ITK a SimpleITK

## SPC_Registration

Python skript, který sdružuje jednotlivé metody. Je možné po jeho spuštění definovat jaká bude použita metoda a metrika. Další možností je spuštění postupně všech implementovaných metod při zvolení jedné metriky. Tato varianta pak uloží výsledky porovnání jednotlivých metod společně s porovnáním času jaký bežely jednotlivé metody.
```
Give examples
```

## Obsah složek

* [Old_tests](https://github.com/duspivao/Semestralni_Prace/tree/master/Old_tests) - Staré původní testy převážně založené na 2D registraci obrazových dat. Využívají především nástroj ITK a jsou zde použity pokusy s vlastní metrikou.
* [Registration_Methods_Using_SITK](https://github.com/duspivao/Semestralni_Prace/tree/master/Registration_Methods_Using_SITK) - Testy s jednotlivými metodami pro registraci 3D obrazových dat. Jsou zde jednotlivě implementované registrační metody MutualInformation,B_Spline metody a metody využívající DemonsRegistrationFilter 
* [SimpleITK_Tests](https://github.com/duspivao/Semestralni_Prace/tree/master/SimpleITK_Tests/) - Dílčí testy
* [Results](https://github.com/duspivao/Semestralni_Prace/tree/master/Results/) - příklady registrovaných 3D snímků


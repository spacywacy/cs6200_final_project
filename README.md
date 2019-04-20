# cs6200_final_project

Goal : To design and build a information retrieval system and also evaluate and compare their performance levels in terms of retrieval effectiveness

Introduction : 
We have used the following retrieval models to build the information retrieval system.
1. Lucene
2. TF/IDF
3. Query Likelihood Model (JM smoothed)
4. BM25

We have modified these retrieval models to make them more efficient by using stemming, stopping techniques. We have applied two query enhancement techniques, that is, pseudo relevance feedback and query time stemming. In order to display the results, snippet generation has also been added. We have also assessed the performance of our retrieval system using MAP, MRR, P@K and Precision and Recall.

Setup and Installation :

The following packages have to be installed.
1. Python 2.7 ( Install from https://www.python.org/downloads/ )
2. Lucence 4.7.2 ( Install from https://lucene.apache.org/ )
3. NLTK 3.4 ( Install from http://www.nltk.org/install.html )
4. BeautifulSoup4 (Install from https://www.crummy.com/software/BeautifulSoup/bs4/doc/ )

Compile and Run :

1. Unzip the Project folder submitted and on the command line navigate to the Project directory.
2. For task 1, 
    1. Run the command 'python Retriever.py'.
    2. The user will be prompted to enter the choice of retrieval model. After the user enters his/her choice, the results will be generated in the results folder.
        1. For Query Likelihood Model, the results for all the 64 queries can be found in the results/QLM folder.  
        2. For TF-IDF, the results for all the 64 queries can be found in the results/TFIDF folder.
        3. For BM25, the results for all the 64 queries can be found in the results/BM25 folder.
    3. For Lucene, follow the steps below.
        1. Create a Java project and add the HW4.java file to the source folder.
        2. Add the jars listed below to the referenced libraries
            1. lucene-core-4.7.2.jar
            2. lucene-queryparser-4.7.2.jar
            3. lucene-analyzers-common-4.7.2.jar
        3. In the HW4.java file, change the variable baseLocation and specify a valid path to where you want to generate the index.
        4. Add the 'parsed-queries.txt' and 'articles' directory to the same location as the baseLocation.
        5. Run the file, the outputs will be generated at the same location in the results folder.
    
3. For task 2,
    1. The folder n10 has the top 10 documents for every query, generated using Lucene.
    2. Run the command 'python pseudo-relevance.py'
    3. This program will generate a file named 'expanded-queries.txt'
    4. Follow the steps described above for lucene by replacing the 'parsed-queries.txt' with the 'expanded-queries.txt' and also in the HW4.java file change 
       the varible queriesFile to 'expanded-queries'
    5. The results will be generated at the same location in the results folder.

  




 
package IR.HW4.LuceneIndex;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Scanner;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.core.SimpleAnalyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.StringField;
import org.apache.lucene.document.TextField;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.index.Term;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopScoreDocCollector;
import org.apache.lucene.store.FSDirectory;
import org.apache.lucene.util.Version;

/**
 * To create Apache Lucene index in a folder and add files into this index based
 * on the input of the user.
 */
public class HW4 {
    private static Analyzer analyzer = new StandardAnalyzer(Version.LUCENE_47);
    private static Analyzer sAnalyzer = new SimpleAnalyzer(Version.LUCENE_47);

    private IndexWriter writer;
    private ArrayList<File> queue = new ArrayList<File>();

    public static void main(String[] args) throws IOException {
    
    String baseLocation = "/Users/nikhilaraya/eclipse-workspace/LuceneIndex/";
	String indexLocation = baseLocation +"index";
	String corpusLocation = baseLocation + "articles";
	
	HW4 indexer = null;
	try {
	    indexer = new HW4(indexLocation);
	} catch (Exception ex) {
	    System.out.println("Cannot create index..." + ex.getMessage());
	    System.exit(-1);
	}

	
	// ===================================================
	// read input from user until he enters q for quit
	// ===================================================
	    try {
		// try to add file into the index
		indexer.indexFileOrDirectory(corpusLocation);
	    } catch (Exception e) {
		System.out.println("Error indexing " + corpusLocation + " : "
			+ e.getMessage());
	    }
	

	// ===================================================
	// after adding, we always have to call the
	// closeIndex, otherwise the index is not created
	// ===================================================
	indexer.closeIndex();

	// =========================================================
	// Now search
	// =========================================================
	
	
	IndexReader reader = DirectoryReader.open(FSDirectory.open(new File(
		indexLocation)));
	IndexSearcher searcher = new IndexSearcher(reader);
	
	File resultsDirectory = new File(baseLocation + "/results");
	if(!resultsDirectory.exists())
		resultsDirectory.mkdir();
	
	Scanner sc = new Scanner(new FileReader("parsed-queries.txt"));
	String query = null;
	int queryId = 0;
	BufferedWriter wr = null;
	while (sc.hasNextLine()) {
		try {
		queryId +=1;
		String fileName = baseLocation + "/results/Lucene-" + queryId;
		wr = new BufferedWriter(new FileWriter(fileName));
		// Changed the code to return 100 results
		TopScoreDocCollector collector = TopScoreDocCollector.create(100, true);
		query = sc.nextLine();
		Query q = new QueryParser(Version.LUCENE_47, "contents",
			analyzer).parse(query);
		searcher.search(q, collector);
		ScoreDoc[] hits = collector.topDocs().scoreDocs;
		String heading = "QueryID\tDocID\tRanking\tScore\n";
		wr.write(heading);
		
		for (int i = 0; i < hits.length; ++i) {
		    int docId = hits[i].doc;
		    Document d = searcher.doc(docId);
		    wr.write(queryId+"\t"+ d.get("path").split("/")[6] 
		    		+"\t"+(i+1)+"\t"+hits[i].score+"\n");
		    
		}
		
		wr.close();
	    } catch (Exception e) {
		System.out.println("Error searching " + query + " : "
			+ e.getMessage());
		break;
	    }
	}

    }

    /**
     * Constructor
     * 
     * @param indexDir
     *            the name of the folder in which the index should be created
     * @throws java.io.IOException
     *             when exception creating index.
     */
    HW4(String indexDir) throws IOException {

	FSDirectory dir = FSDirectory.open(new File(indexDir));

	IndexWriterConfig config = new IndexWriterConfig(Version.LUCENE_47,
		analyzer);

	writer = new IndexWriter(dir, config);
    }

    /**
     * Indexes a file or directory
     * 
     * @param fileName
     *            the name of a text file or a folder we wish to add to the
     *            index
     * @throws java.io.IOException
     *             when exception
     */
    public void indexFileOrDirectory(String fileName) throws IOException {
	// ===================================================
	// gets the list of files in a folder (if user has submitted
	// the name of a folder) or gets a single file name (is user
	// has submitted only the file name)
	// ===================================================
	addFiles(new File(fileName));

	int originalNumDocs = writer.numDocs();
	for (File f : queue) {
	    FileReader fr = null;
	    try {
		Document doc = new Document();

		// ===================================================
		// add contents of file
		// ===================================================
		fr = new FileReader(f);
		doc.add(new TextField("contents", fr));
		doc.add(new StringField("path", f.getPath(), Field.Store.YES));
		doc.add(new StringField("filename", f.getName(),
			Field.Store.YES));

		writer.addDocument(doc);
		System.out.println("Added: " + f);
	    } catch (Exception e) {
		System.out.println("Could not add: " + f);
	    } finally {
		fr.close();
	    }
	}

	int newNumDocs = writer.numDocs();
	System.out.println("");
	System.out.println("************************");
	System.out
		.println((newNumDocs - originalNumDocs) + " documents added.");
	System.out.println("************************");

	queue.clear();
    }

    private void addFiles(File file) {

	if (!file.exists()) {
	    System.out.println(file + " does not exist.");
	}
	if (file.isDirectory()) {
	    for (File f : file.listFiles()) {
		addFiles(f);
	    }
	} else {
	    String filename = file.getName().toLowerCase();
	    // ===================================================
	    // Only index text files
	    // ===================================================
	    if (filename.endsWith(".htm") || filename.endsWith(".html")
		    || filename.endsWith(".xml") || filename.endsWith(".txt")) {
		queue.add(file);
	    } else {
		System.out.println("Skipped " + filename);
	    }
	}
    }

    /**
     * Close the index.
     * 
     * @throws java.io.IOException
     *             when exception closing
     */
    public void closeIndex() throws IOException {
	writer.close();
    }
}

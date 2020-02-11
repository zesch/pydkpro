package example;

import com.google.gson.Gson;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import org.apache.uima.UIMAException;
import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.fit.factory.JCasFactory;
import org.apache.uima.jcas.JCas;


// @DKPRO import code generation is starting this line


import java.util.ArrayList;
import java.util.List;


import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngine;


import java.io.ByteArrayOutputStream;
import org.apache.uima.util.XMLSerializer;
import org.apache.uima.cas.CAS;
import org.apache.uima.cas.TypeSystem;
import org.apache.uima.cas.impl.XmiCasSerializer;

public class DKProPipeline {
   //private static final String COUNTS_PATH = PhraseAnnotationPipeline.class.getClassLoader().getResource("counts.xz");
   //private static final String COUNTS_PATH = "counts.xz";
    public static void main(String[] args)
            throws Exception {
        DKProPipeline analysis = new DKProPipeline();
        analysis.run( analysis.createParamString() );
    }

    public JCas run(String jsonString) throws Exception {
        /* a lower threshold yields more multi-token phrases */
   //     float threshold = (float) 100.0;
        System.out.println("Guiya");

        // setup gson parser
        JsonParser parser = new JsonParser();
        JsonElement jsonElement = parser.parse(jsonString);
        JsonObject jsonObject = jsonElement.getAsJsonObject();
        System.out.println(jsonObject);

        // get parameters out of the json object
        String text = jsonObject.get("text").toString();
        System.out.println(text);

        // create analysis engines
        // @DKPRO create pipeline components analysis, starting this line


        // List all engines in an iterator
        List<AnalysisEngine> engines = new ArrayList<AnalysisEngine>();

        // @DKPRO add pipeline components analysis, starting this line



        // JWeb1TIndexer indexCreator = new JWeb1TIndexer(outpcd .. utLocation, 3);
        JCas jcas = process(text, engines);
        System.out.println(jcas);
        System.out.println(JCasToXMIString(jcas));
        return jcas;
    }

    // return Jcas after iterated over all given engines
    private JCas process(String aText, List<AnalysisEngine> engines) throws UIMAException {

        JCas jcas = JCasFactory.createText(aText, "en");

        for (AnalysisEngine engine : engines)
            engine.process(jcas);

        return jcas;
    }

    private String createParamString() {

        FrequencyCountParameter paramter = new FrequencyCountParameter();
        // tokenizedParameter.language = "de";
        paramter.text = "Bacon ipsum dolor amet picanha porchetta boudin, jowl tail biltong brisket corned beef turducken beef meatloaf. Ball tip buffalo ham hock ribeye bresaola short loin swine shankle doner frankfurter. Pork loin short ribs salami ground round sausage short loin beef shank cow ham chuck rump buffalo leberkas. Bresaola alcatra cupim ham, shankle tongue beef ribs porchetta filet mignon leberkas venison prosciutto pork chuck. ";
        System.out.println(new Gson().toJson(paramter));
        return new Gson().toJson(paramter);
    }
    
    
    private static String JCasToXMIString(JCas result) throws Exception {

        ByteArrayOutputStream outStream = null;

        try {
            // create out stream
            outStream = new ByteArrayOutputStream();
            XMLSerializer xmlSer = new XMLSerializer(outStream, false);
            // create cas from jcas (result)
            CAS resultCas = result.getCas();

            // get current cas type system
            TypeSystem resultType = resultCas.getTypeSystem();

            // set up CAS serializer with type system
            XmiCasSerializer xmi_cas = new XmiCasSerializer(resultType);


            xmi_cas.serialize(resultCas, xmlSer.getContentHandler());

            String resultXMLString = outStream.toString();

            return resultXMLString;


        } catch (Exception e) {

            e.printStackTrace();
            return "JCas to String hat nicht funktioniert";

        } finally {

            if (outStream != null) {
                outStream.close();
            }
        }
    }
}

package com;
// @DKPRO CLI import code generation is starting this line



import org.apache.uima.cas.CAS;
import org.apache.uima.cas.TypeSystem;
import org.apache.uima.cas.impl.XmiCasSerializer;
import org.apache.uima.jcas.JCas;

import org.apache.uima.util.XMLSerializer;
import org.springframework.web.bind.annotation.*;

import java.io.ByteArrayOutputStream;

@RestController
public class DKProEndpoint {
    // @DKPRO CLI init static analysis, starting this line
        
    @RequestMapping(
            value = "/analysis", method = RequestMethod.POST, consumes = "application/json")
    public static String analyzeText(@RequestBody String jsonString) throws Exception {
            
            // @DKPRO CLI analysis code generation is starting this line
            

            return JCasToXMIString(result);


    }

    @RequestMapping(
            value = "/testPage", method = RequestMethod.POST, consumes = "application/json")
    public static String testPageMethod(@RequestBody String jsonString) throws Exception {


            return "OK";


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


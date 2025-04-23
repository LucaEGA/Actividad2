package ar.edu.udeci.pv;

import org.apache.commons.cli.*;
import org.apache.log4j.Logger;

public class CLIExample {
    static Logger logger = Logger.getLogger(CLIExample.class);

    public static void main(String[] args) {
        logger.info("La aplicación comenzó");

        Options options = new Options();

        Option help = new Option("h", "help", false, "Muestra ayuda");
        options.addOption(help);

        CommandLineParser parser = new DefaultParser();

        try {
            CommandLine cmd = parser.parse(options, args);

            if (cmd.hasOption("h")) {
                HelpFormatter formatter = new HelpFormatter();
                formatter.printHelp("Actividad2", options);
            } else {
                System.out.println("No se pasó la opción -h");
            }
        } catch (ParseException e) {
            logger.error("Error al parsear los argumentos", e);
        }
    }
}

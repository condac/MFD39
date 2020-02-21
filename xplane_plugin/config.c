#include "openSimIO.h"
#include "config.h"

extern pin_struct *pins;

void readConfig() {
   nrOfLines = 0;
   nrOfPins = 0;
   if ((configFile = fopen("Resources/plugins/MFD39/config.txt", "r")) == NULL) {
      display("Error! opening configfile");

   } else {

      char *line = NULL;
      size_t len = 0;
      ssize_t read;

      while ((read = getline(&line, &len, configFile)) != -1) {
         nrOfLines++;
      }
      fclose(configFile);

      //display("lines in config file %d", nrOfLines);

      pins = malloc(nrOfLines * sizeof(pin_struct));

      if ((configFile = fopen("Resources/plugins/MFD39/config.txt", "r")) == NULL) {
         display("Error! opening configfile");

      } else {
         char *line = NULL;
         size_t len = 0;
         ssize_t read;
         while ((read = getline(&line, &len, configFile)) != -1) {
            //display("%s", line);
            pin_struct *newPin = lineToStruct(line);
            if (newPin != NULL) {
               memcpy(pins + nrOfPins, newPin, sizeof(pin_struct));
               nrOfPins++;
            }
         }
      }
   }

}

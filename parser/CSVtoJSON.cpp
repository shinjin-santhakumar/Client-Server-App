#include <fstream>
#include <iostream>
#include <vector>
#include <string>

bool prepareFiles(std::ifstream& in, std::ofstream& out);
std::vector<std::string> prepareCats(std::ifstream& in);
unsigned long parse(bool vis, std::ifstream& in, std::ofstream& out, std::vector<std::string>& cats);
std::string indent(unsigned int amt);
void readCurrentLine(bool vis, std::string& ref, std::vector<std::string>& bin);

int main() {
    std::ifstream reader;
    std::ofstream writer;

    std::cout << "Please ensure your .CSV file is in the correct location before starting.\n"
              << "         File path: .\\Files\\input\\" << std::endl;

    //----- Error Check -----
    //  Runs the prepareFiles() function until the user aborts the program or inputs a correct title.
    //-----------
    while (!prepareFiles(reader, writer)) {
        std::cout << "There was an error opening your files.\nPlease try again, or use CTRL + C to abort." << std::endl;
        reader.close();
        writer.close();
        reader.clear();
        writer.clear();
    }
    //-----------------------

    std::vector<std::string> categories = prepareCats(reader);

    //----- Visual Toggle -----
    //  Prompts the user on whether or not they would like to see the data during the process.
    //  Has built-in error checking to prevent invalid input.
    //------------
    char choice;
    bool visuals = false;
    std::cout << "\nThe program is ready to translate your file.\n"
        << "Would you like to see the data while it is being parsed? (Y/N): ";
    std::cin >> choice; choice = toupper(choice);
    while (choice != 'Y' && choice != 'N') {
        std::cout << "Invalid response. Please enter Y for Yes or N for No.\n";
        std::cin >> choice;
    }
    if (choice == 'Y') { visuals = true; }
    //-------------------------
    
    std::cout << "\nNow translating...\n";
    unsigned long total = parse(visuals, reader, writer, categories);

    reader.close();
    writer.close();

    std::cout << "The file was translated successfully.\n"
              << total << " lines of data were analyzed.\n"
              << "         File path: .\\Files\\output\\" << std::endl;

    return 0;
}

//----- prepareFiles() -----
//  Passes in an input stream by reference and an output stream by reference.
//  Prompts the user for a file name, then attempts to open that file for both instream and outstream.
//  Returns TRUE if opening the file was successful, FALSE otherwise.
//------------
bool prepareFiles(std::ifstream& in, std::ofstream& out) {
    std::string inFile = ".\\Files\\input\\";
    std::string outFile = ".\\Files\\output\\";
    std::string fileName;

    std::cout << "\nEnter the file to translate to JSON (Do not include the file type): ";
    std::cin >> fileName;
    unsigned int nameSize = fileName.size();

    fileName.append(".csv");
    inFile += fileName;

    fileName.resize(nameSize);
    fileName.append(".json");
    outFile += fileName;

    in.open(inFile);
    out.open(outFile);

    if (in.fail() || out.fail()) { return false; }
    else { return true; }
}
//--------------------------

//----- prepareCats() -----
//  Passes in an input stream by reference.
//  Reads the first line of the csv file and creates a vector of strings containing all of the first values (categories)
//  Requires that the passed-in input stream already has a file opened.
//  Returns the completed vector of category strings.
//------------
std::vector<std::string> prepareCats(std::ifstream& in) {
    std::vector<std::string> retVec;
    retVec.reserve(15);
    std::string firstLine;
    std::getline(in, firstLine);

    std::cout << "\nCategories:\n";

    if (in.good()) {
        std::string catBuilder = "";
        for (unsigned i = 0; i < firstLine.size(); ++i) {
            if (firstLine.at(i) == '\"') { catBuilder.append("\\\""); }
            else if (firstLine.at(i) == '\\') { catBuilder.append("\\\\"); }
            else if (firstLine.at(i) != ',' && static_cast<int>(firstLine.at(i)) > 31) { catBuilder.push_back(firstLine.at(i)); }
            else {
                retVec.push_back(catBuilder);
                std::cout << "   " << retVec.size() << ".   " << retVec.back() << "\n";
                catBuilder.clear();
            }
        }
        std::cout << std::endl;
    }
    else {
        std::cout << "An error occurred while reading the file!\n";
        exit(1);
    }

    return retVec;
}
//-------------------------

//----- parse() -----
//  Passes in a boolean, input stream by reference, output stream by reference, and vector of category strings by reference.
//  Reads and formats .csv data into the corresponding .json file.
//  Calls readCurrentLine() to copy correct data values.
//  If passed-in boolean is TRUE, prints the number of each line in the .csv as it is read. Prints nothing otherwise.
//  Requires that the passed-in input and output streams already have a file opened.
//  Returns the number of .csv lines that were translated.
//---------
unsigned long parse(bool vis, std::ifstream& in, std::ofstream& out, std::vector<std::string>& cats) {
    unsigned long retVal = 0;
    unsigned int tab = 1;
    std::string readingLine;
    std::vector<std::string> lineVals;
    lineVals.reserve(cats.size());

    out << "[\n";
    while (std::getline(in, readingLine)) {
        if (!in.fail()) {
            ++retVal;
            if (vis) { std::cout << "Reading entry number " << retVal << "...\n"; }
            readCurrentLine(vis, readingLine, lineVals);
            out << indent(tab) << "{\n"; ++tab;
            for (unsigned i = 0; i < cats.size(); ++i) {
                if ((i + 1) == cats.size()) { out << indent(tab) << "\"" << cats.at(i) << "\": \"" << lineVals.at(i) << "\"\n"; }
                else { out << indent(tab) << "\"" << cats.at(i) << "\": \"" << lineVals.at(i) << "\",\n"; }
            }
            if (in.peek() != -1) { --tab; out << indent(tab) << "},\n"; }
            else { --tab; out << indent(tab) << "}\n"; }
            lineVals.clear();
        }
    }
    out << "]\n";

    return retVal;
}
//-------------------

//----- indent() -----
//  Helper function for parse().
//  Passes in an unsigned integer.
//  Returns a string containing that many tabs.
//----------
std::string indent(unsigned int amt) {
    std::string retVal = "";
    for (unsigned i = 0; i < amt; ++i) {
        retVal += "\t";
    }
    return retVal;
}
//---------------------

//----- readCurrentLine() -----
//  Helper function for parse().
//  Passes in a boolean, string by reference, and vector of strings by reference.
//  Reads the string in .csv format, splices the data into the vector of strings.
//  If passed-in boolean is TRUE, outputs the data as it is being spliced. Prints nothing otherwise.
//  Returns nothing.
//--------------
void readCurrentLine(bool vis, std::string& ref, std::vector<std::string>& bin) {
    std::string val = "";
    bool openQuotes = false;
    for (unsigned i = 0; i < ref.size(); ++i) {
        if (charValid(ref.at(i))) {
            if (ref.at(i) == '\"') {
                val.append("\\\"");
                if (!openQuotes) { openQuotes = true; }
                else { openQuotes = false; }
            }
            else if (ref.at(i) == '\\') { val.append("\\\\"); }
            else if (ref.at(i) != ',' || openQuotes) { val.push_back(ref.at(i)); }
            else {
                bin.push_back(val);
                if (vis) { std::cout << "   " << bin.size() << ".   " << bin.back() << "\n"; }
                val.clear();
            }
        }
    }
    if (vis) { std::cout << std::endl; }
}
//------------------------------

//----- charValid() -----
// Helper function for readCurrentLine().
// Passes in a character.
// Returns TRUE if the character is Ascii. FALSE otherwise.
//-----------------------
bool charValid(char c) {
    if (static_cast<int>(c) > 31 && static_cast<int>(c) < 127) { return true; }
    else { return false; }
}
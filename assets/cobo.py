#!/usr/bin/env python3
# cobo.py
# SLD 2021
#



############
# INITIALIZATION
############

# Imports
import os, sys, json
from datetime import datetime

# Greet the user
print("COBO, a cookbook (and cookbook build system) \nSLD 2021 \n")

# Valid operation modes go here
valid_modes = ["help", "build", "get-tags", "subset", "compile-md", "add-source"]

# Set constants
MD_LINEBREAK = "\n\n"

# Initialize variables
source_dir = None
dest_dir = None
input_filename = None
output_filename = None
tag = None
mode = None

# Begin parsing command line arguments
# First, collect operation mode
try: mode = sys.argv[1].lower()
except: pass

# Parse mode-dependent variables
for raw_arg in sys.argv[2:]:
    this_arg = raw_arg.split("=")

    # Variables should occupy one argument, form of `ARG=VALUE`
    if len(this_arg) == 2:
        this_var = this_arg[0].lower()
        this_val = this_arg[1]

        # Assign variable values
        if this_var == "sources": source_dir = this_val
        if this_var == "input": input_filename = this_val
        if this_var == "output": output_filename = this_val
        if this_var == "tag": tag = this_val
        if this_var == "dest": dest_dir = this_val

# Ensure mode has been specified or quit
if(mode) and mode in valid_modes: pass
else: quit("Valid operation mode required but not defined. Valid modes:\n\n"+
            "\n".join("`"+md+"`" for md in valid_modes)+
            "\n")

# Test that all required arguments have been passed before continuing
# `update` requires `sources=<<<SOURCE_DIR>>>` and `output=<<<OUTPUT_FILE>>>`
print("Operation mode: `"+mode+"`")
if mode == "build":
    if(source_dir): pass
    else: quit("Source directory required but not defined: try adding `sources=SOURCE_DIR`\n")
    if(output_filename): pass
    else: quit("Output filename required but not defined: try adding `output=OUTPUT_FILE`\n")
if mode == "get-tags":
    if(input_filename): pass
    else: quit("Input filename required but not defined: try adding `input=INPUT_FILE`\n")
    if(output_filename): pass
    else: quit("Output filename required but not defined: try adding `output=OUTPUT_FILE`\n")
if mode == "subset":
    if(tag): pass
    else: quit("Tag required but not defined: try adding `tag=TAG`\n")
    if(input_filename): pass
    else: quit("Input filename required but not defined: try adding `input=INPUT_FILE`\n")
    if(output_filename): pass
    else: quit("Output filename required but not defined: try adding `output=OUTPUT_FILE`\n")
if mode == "compile-md":
    if(input_filename): pass
    else: quit("Input filename required but not defined: try adding `input=INPUT_FILE`\n")
    if(output_filename): pass
    else: quit("Output filename required but not defined: try adding `output=OUTPUT_FILE`\n")
if mode == "add-source":
    if(dest_dir): pass
    else: quit("Destination directory required but not defined: try adding `dest=DEST_DIR`\n")


############
# OPERATION MODE `help`
############
if mode == "help":
    print("\nSyntax: python3 cobo.py OP_MODE ARG1 ARG2 ... ARGn")
    print()
    print("OP_MODE `help`: displays this help screen")
    print()
    print("OP_MODE `build`: build output JSON file from contents of a source directory")
    print("\tRequired argument `sources`: specifies directory containing source MD files")
    print("\tRequired argument `output`: specifies JSON output file name")
    print()
    print("OP_MODE `get-tags`: extract tags from input JSON file and output as plaintext file")
    print("\tRequired argument `input`: specifies JSON input file name")
    print("\tRequired argument `output`: specifies plaintext output file name")
    print()
    print("OP_MODE `subset`: extract subset of input JSON file by tag, and output as JSON file")
    print("\tRequired argument `tag`: specifies tag to extract recipes by")
    print("\tRequired argument `input`: specifies JSON input file name")
    print("\tRequired argument `output`: specifies JSON output file name")
    print()
    print("OP_MODE `compile-md`: compile Markdown cookbook from an input JSON file")
    print("\tRequired argument `input`: specifies JSON input file name")
    print("\tRequired argument `output`: specifies Markdown output file name")
    print()
    print("OP_MODE `add-source`: add new blank Markdown recipe to the specified source directory")
    print("\tRequired argument `dest`: specifies destination directory for new MD file")
    print()
    quit()


############
# OPERATION MODE `build`
############
if mode == "build":

    # Begin by polling the source directory for MD files
    files = os.listdir(source_dir+"/")
    recipes_to_parse=[]
    for indiv_file in files:
        if indiv_file[-2:].lower()=="md":
            recipes_to_parse.append(source_dir+"/"+indiv_file)

    # Begin collecting data
    data = {}
    for this_recipe in recipes_to_parse:

        # For this recipe, get the entire recipe body
        input_file = open(this_recipe, "r")
        full_text = [ln.strip("\n") for ln in input_file.readlines()]
        input_file.close()

        # Extract title, tags, and method
        title = full_text[0][2:]
        tags = [tg[1:-1] for tg in full_text[2][1:-1].split(",")]
        method = full_text[4:]

        # Define index (hash) and handle (derived from title)
        # Need these for downstream data manipulation and file creation
        index = this_recipe.split("/")[-1:][0][:-3]
        handle = "-".join(title.lower().split())

        data[index] = {
            "handle":handle,
            "title":title,
            "tags":tags,
            "method":method
        }

    # Create JSON dump and write out
    with open(output_filename, "w") as output_file:
        output_file.write(json.dumps(data, indent=4))

    # Clean up and finish
    output_file.close()
    quit("Successfully built `"+output_filename+"` from contents of `"+source_dir+"` \n")



############
# OPERATION MODE: `get-tags`
############
if mode == "get-tags":

    # Begin by loading the JSON input file
    input_file = open(input_filename, "r")
    data = json.load(input_file)
    input_file.close()

    # Pass through each recipe
    all_tags = []
    for index in data:

        # Get the tags from this recipe
        this_recipe_tags = data[index]["tags"]

        # Add tags from this recipe to the global list if not already present
        for this_tag in this_recipe_tags:
            if this_tag not in all_tags: all_tags.append(this_tag)

    # Export tag list
    output_file = open(output_filename, "w")
    for this_tag in all_tags: output_file.write(this_tag+"\n")

    # Clean up and finish
    output_file.close()
    quit("Successfully extracted tags from `"+input_filename+"` to `"+output_filename+"` \n")



#########
# OPERATION MODE: `subset`
############
if mode == "subset":

    # Begin by loading the JSON input file
    input_file = open(input_filename, "r")
    data = json.load(input_file)
    input_file.close()

    # Collect recipe indices citing the specified tag
    tagged_indices = []
    for index in data:
        if tag in data[index]["tags"]: tagged_indices.append(index)

    # Clone tagged recipes into a new dictionary
    subset_data = {}
    for this_index in tagged_indices:

        # Get the data for this recipe
        this_handle = data[this_index]["handle"]
        this_title = data[this_index]["title"]
        this_tags = data[this_index]["tags"]
        this_method = data[this_index]["method"]

        # Add to the subset dictionary
        subset_data[this_index] = {
            "handle":this_handle,
            "title":this_title,
            "tags":this_tags,
            "method":this_method
        }

    # Create JSON dump and write out
    with open(output_filename, "w") as output_file:
        output_file.write(json.dumps(subset_data, indent=4))

    # Clean up and finish
    output_file.close()
    quit("Successfully built `"+output_filename+"` from `"+input_filename+"` using tag `"+tag+"` \n")



#########
# OPERATION MODE: `compile-md`
############
if mode == "compile-md":

    # Begin by loading the JSON input file
    input_file = open(input_filename, "r")
    data = json.load(input_file)
    input_file.close()

    # Pass through recipe indices
    toc = ""
    contents = ""
    for index in data:

        # Create title text and ToC link
        title_text = "## " + data[index]["title"]
        toc += "["+data[index]["title"]+"](#"
        toc += "-".join(data[index]["title"].lower().split())
        toc += ")\\\n"

        # Create metadata text
        metadata_text =  "#### COBO Metadata"
        metadata_text += "\n```\n"
        metadata_text += "index:"    + index                     + "\n"
        metadata_text += "handle:"   + data[index]["handle"]     + "\n"
        metadata_text += "tags:"     + str(data[index]["tags"])  + "\n"
        metadata_text += "```"

        # Create method text
        method_text = ""
        for line in data[index]["method"]: method_text += line + "\n"

        # Add recipe to contents text
        contents += " ___ \n"
        contents += title_text
        contents += MD_LINEBREAK
        contents += metadata_text
        contents += MD_LINEBREAK
        contents += method_text
        contents += MD_LINEBREAK + MD_LINEBREAK


    # Create Markdown file and write out
    output_file = open(output_filename, "w")
    output_file.write(
        "## Table Of Contents: ```" + input_filename+"```"
        +MD_LINEBREAK
        +toc
        +MD_LINEBREAK
        +contents
    )

    # Clean up and finish
    output_file.close()
    quit("Successfully compiled `"+input_filename+"` to `"+output_filename+"` \n")



#########
# OPERATION MODE: `add-source`
############
if mode == "add-source":

    # Generate a new source filename
    dt_obj = datetime.now()
    new_source =    str(dt_obj.day).zfill(2)
    new_source +=   str(dt_obj.month).zfill(2)
    new_source +=   str(dt_obj.year).zfill(4)
    new_source +=   str(dt_obj.second).zfill(2)
    new_source +=   str(dt_obj.minute).zfill(2)
    new_source +=   str(dt_obj.hour).zfill(2) + ".md"

    # Clone recipe template into source directory, named as new source
    os.system("cp ./source.md.template "+dest_dir+"/"+new_source)

    # Clean up and finish
    quit("Successfully created new source `"+dest_dir+"/"+new_source+"` \n")

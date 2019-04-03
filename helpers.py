def generateStartup(key):
    startup = open("uploads/startups/"+key+"-startup.xml","w+")
    startup_content = """
<aiml version="1.0.1" encoding="UTF-8">
    <!-- std-startup.xml -->

    <!-- Category is an atomic AIML unit -->
    <category>
        <pattern>LOAD AIML B</pattern>
        <template>
            <learn>uploads/aiml/"""+key+""".aiml</learn>
        </template>
    </category>
</aiml>
    """
    try:
        startup.write(startup_content)
        return True
    except Exception as e:
        return False


def generateAIML(qf,af,key):
    aiml_file = open("uploads/aiml/"+key+".aiml","w+")
    aiml_start = """<aiml version="1.0.1" encoding="UTF-8">
    <!-- basic_chat.aiml -->
    """
    for x,y in zip(qf,af):
        x = x.strip().replace('?','').replace('.','').upper()
        y = y.strip()
        aiml_start += """<category>
                    <pattern>"""+x+ """</pattern>
                    <template>"""+y+ """</template>
                    </category>
        """
    aiml_start += "</aiml>"
    aiml_file.write(aiml_start)
    return True

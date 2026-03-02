from getData.ecos.services.statisticWord import statisticWord

def searchWord(word: str):
    result = statisticWord(word=word)
    word = result.get('WORD')
    content = result.get('CONTENT')
    print(f"word : content")
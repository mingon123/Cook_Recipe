import urllib.request
import json
import pandas as pd

ServiceKey = "8e3850cacf8a4d7d9aa2"

def getRequestUrl(url):
    req = urllib.request.Request(url)
    try:
        response = urllib.request.urlopen(req)
        if response.getcode() == 200:
            print("Url Request Success")
            return response.read().decode('utf-8')
    except Exception as e:
        print(e)
        print("Error for URL : %s" % url)
        return None

def getRecipesData(url):
    responseDecode = getRequestUrl(url)
    if responseDecode == None:
        return None
    else:
        data = json.loads(responseDecode)
        recipes = data.get("COOKRCP01", {}).get("row", [])
        parsed_recipes = []

        for recipe in recipes:
            articleNo = recipe.get("RCP_SEQ", "")
            recipe_name = recipe.get("RCP_NM", "")
            recipe_ingredients = recipe.get("RCP_PARTS_DTLS", "")
            recipe_method = recipe.get("RCP_WAY2", "")
            recipe_type = recipe.get("RCP_PAT2", "")
            recipe_calories = recipe.get("INFO_ENG", "")
            recipe_carbs = recipe.get("INFO_CAR", "")
            recipe_protein = recipe.get("INFO_PRO", "")
            recipe_fat = recipe.get("INFO_FAT", "")
            recipe_sodium = recipe.get("INFO_NA", "")
            att_file_no_mk = recipe.get("ATT_FILE_NO_MK", "")
            rcp_na_tip = recipe.get("RCP_NA_TIP", "")

            manual1 = recipe.get("MANUAL01", "")
            manual2 = recipe.get("MANUAL02", "")
            manual3 = recipe.get("MANUAL03", "")
            manual4 = recipe.get("MANUAL04", "")
            manual5 = recipe.get("MANUAL05", "")
            manual6 = recipe.get("MANUAL06", "")


            manual_img1 = recipe.get("MANUAL_IMG01", "")
            manual_img2 = recipe.get("MANUAL_IMG02", "")
            manual_img3 = recipe.get("MANUAL_IMG03", "")
            manual_img4 = recipe.get("MANUAL_IMG04", "")
            manual_img5 = recipe.get("MANUAL_IMG05", "")
            manual_img6 = recipe.get("MANUAL_IMG06", "")


            parsed_recipe = {
                "번호": articleNo,
                "메뉴명": recipe_name,
                "재료": recipe_ingredients,
                "조리방법": recipe_method,
                "요리종류": recipe_type,
                "열량": int(round(float(recipe_calories))),
                "탄수화물": int(round(float(recipe_carbs))),
                "단백질": int(round(float(recipe_protein))),
                "지방": int(round(float(recipe_fat))),
                "나트륨": int(round(float(recipe_sodium))),
                "완성이미지": att_file_no_mk,
                "저감조리법_TIP": rcp_na_tip,
                "조리순서1": manual1,
                "이미지1": manual_img1,
                "조리순서2": manual2,
                "이미지2": manual_img2,
                "조리순서3": manual3,
                "이미지3": manual_img3,
                "조리순서4": manual4,
                "이미지4": manual_img4,
                "조리순서5": manual5,
                "이미지5": manual_img5,
                "조리순서6": manual6,
                "이미지6": manual_img6
            }
            parsed_recipes.append(parsed_recipe)

        return parsed_recipes

def main():
    url = "https://openapi.foodsafetykorea.go.kr/api/8e3850cacf8a4d7d9aa2/COOKRCP01/json/1001/1124"
    recipes_data = getRecipesData(url)

    if recipes_data:
        # JSON 파일로 저장
        with open('recipes_data2.json', 'w', encoding='utf-8') as json_file:
            json.dump(recipes_data, json_file, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()

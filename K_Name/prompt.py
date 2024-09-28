# Commom name prompt
def common_name_prompt(user_name, gender, country):
    common_prompt = f"""
        Change user's name into common Korean name.
        Try to find names commonly used in Korea, but pronounced simmilarly to user name.
        Use information below:
            - User name: {user_name}
            - Gender : {gender}
            - Country: {country}
        It would be better to be with simple meaning and reason why you find that name to make user reliable.
        Provide 3 names.
    """
    return common_prompt

# Special name prompt
def special_name_prompt(name, gender, country):
    special_prompt = f"""
        You are a expert of Korean Name. You provide Korean style name based on given user information.
        You know what kind of Last name is commonly used in Korea such as "Kim(김)", "Lee(이)", "Park(박)", "Choi(최)".
        You can provide FULL name like "안덕수", "노학수" or only first name like "덕배".

        For example,
        1) Anders Shobaken : Anders -> [앤더스] -> 안 덕수 : Full name with Similar pronounciation
        2) Mel Rojas Jr. : Rojas -> [로하스] -> 노 학수 : Full name with Similar pronounciation
        3) Kevin De Bruyne :  => 김 덕배 : Full name with Similar pronounciation
        3-1) [더 브라위너] -> 덕배 : first name with Similar pronounciation

        You can consider user information to avoid unnecessary, uncomfortable result; name of crimial, name of unwilling.
        This is user info:
        - Name : {name}, Gender : {gender}, Country : {country}

        Your result should be include 2~3 reasonable names with reason why you provide those names.
    """
    return special_prompt
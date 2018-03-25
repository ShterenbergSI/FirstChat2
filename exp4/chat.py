import requests, re
from hashlib import sha1
from xml.dom.minidom import parseString

def main():
    login = "" # здесь введите свой логин
    password = "" # а здесь - пароль
    session = authorize(login, password)
    print_messages(session)

def authorize(login, password):
    session = requests.Session()
    index = session.get("http://forum.hellroom.ru/index.php")
    session_id = re.search("hashLoginPassword\(this, '(.+?)'\)", index.text).group(1)
    hash_password = hashLoginPassword(login, password, session_id)
    login_response = session.post("http://forum.hellroom.ru/index.php?action=login2", data = {
        "user": login, "passwrd": "", "coockielength": -1, "hash_passwrd": hash_password
    })
    return session

def print_messages(session):
    address = "http://forum.hellroom.ru/index.php?action=shoutbox;sa=get;xml;row=0;restart"
    xml = session.get(address).text
    for msg in parse_messages(xml):
        print(msg["user"], msg["date"], msg["text"])

def parse_messages(xml):
    outer_document = parseString(xml)
    msgs_node = outer_document.getElementsByTagName("msgs")[0]
    msgs = msgs_node.firstChild.nodeValue
    msgs = "<msgs>" + msgs.replace("</div>", "</span>") + "</msgs>"
    document = parseString(msgs)
    for node in document.getElementsByTagName("tr"):
        user = node.getElementsByTagName("a")[0].firstChild.nodeValue
        date = node.getElementsByTagName("span")[0].firstChild.nodeValue
        text = node.getElementsByTagName("span")[1].firstChild.nodeValue
        if not text:
            text = ""
        yield {"user": user, "date": date, "text": text}

def hashLoginPassword(login, password, session_id):
    return sha1(sha1(php_to8bit(login).lower() + php_to8bit(password)).hexdigest().encode("ascii")
                + session_id.encode("ascii")).hexdigest()

def php_to8bit(string):
    res = b""
    byte = lambda i: bytes((i,))
    for n in (ord(c) for c in string):
        if n < 128:
            res += byte(n)
        elif n < 2048:
            res += byte(192 | n >> 6) + byte(128 | n & 63)
        elif n < 65536:
            res += byte(224 | n >> 12) + byte(128 | n >> 6 & 63) + byte(128 | n & 63)
        else:
            res += byte(240 | n >> 18) + byte(128 | n >> 12 & 63) + byte(128 | n >> 6 & 63) + byte(128 | n & 63)
    return res

if __name__ == "__main__":
    main()
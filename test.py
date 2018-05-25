from application import newItem

def test_new_item():
    assert type(newItem(2)) == isinstance(Item)
from zlibrary import AsyncZlib, booklists
import asyncio
import logging
import os

logging.getLogger("zlibrary").addHandler(logging.StreamHandler())
logging.getLogger("zlibrary").setLevel(logging.DEBUG)


async def main():
    # ensure environment variables are set
    zlogin = os.environ.get('ZLOGIN')
    zpassw = os.environ.get('ZPASSW')
    assert zlogin is not None, "ZLOGIN environment variable is not set"
    assert zpassw is not None, "ZPASSW environment variable is not set"

    lib = AsyncZlib()
    await lib.login(zlogin, zpassw)

    # ensure profile is initialized
    assert hasattr(lib, 'profile') and lib.profile is not None, "lib.profile is not initialized after login"

    # fleshed out booklist search
    booklist_paginator = await lib.profile.search_public_booklists("test")
    assert booklist_paginator is not None, "Booklist paginator is None"
    booklists = await booklist_paginator.next()
    assert isinstance(booklists, list), "Booklists is not a list"
    assert len(booklists) > 0, "No booklists found"
    print(f"Found {len(booklists)} public booklists matching 'test':")
    for idx, bl in enumerate(booklists, 1):
        assert 'name' in bl and bl['name'], f"Booklist {idx} missing name"
        assert 'url' in bl and bl['url'], f"Booklist {idx} missing url"
        print(f"[{idx}] Name: {bl.get('name')}, ID: {bl.get('url')}, Description: {bl.get('description')}, Books: {bl.get('count')}, Views: {bl.get('views')}")
    
    # fetch books from the first booklist
    first_booklist = booklists[0]
    await first_booklist.fetch()
    books_in_list = first_booklist.storage.get(1, [])
    assert isinstance(books_in_list, list), "Books in list is not a list"
    print(f"First booklist contains {len(books_in_list)} books. Example:")
    for i, book in enumerate(books_in_list[:3], 1):
        assert 'name' in book and book['name'], f"Book {i} missing name"
        assert 'id' in book and book['id'], f"Book {i} missing id"
        print(f"  - {book.get('name')} (ID: {book.get('id')})")

    # count: 10 results per set
    paginator = await lib.search(q="biology", count=10)
    await paginator.next()

    assert len(paginator.result) > 0
    print(paginator.result)

    # fetching next result set (10 ... 20)
    next_set = await paginator.next()

    assert len(next_set) > 0
    print(next_set)

    # get back to previous set (0 ... 10)
    prev_set = await paginator.prev()

    assert len(prev_set) > 0
    print(prev_set)

    book = await paginator.result[0].fetch()
    assert book.get('name')
    print(book)

    book = await lib.get_by_id('5393918/a28f0c')
    assert book.get('name')
    print(book)


if __name__ in '__main__':
    asyncio.run(main())

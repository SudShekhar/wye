import pytest

from .. import factories as f

pytestmark = pytest.mark.django_db


public_pages = [
    '/',
    '/about/',
    '/faq/',
    '/accounts/login/',
    '/accounts/signup/',
    '/accounts/password/reset/',
]

restricted_pages = [
    '/organisation/',
    '/organisation/create/',
    '/workshop/',
    '/workshop/create/',
]

staff_pages = [
    '/region/',
    '/region/lead/create/',
    '/region/location/create/',
    '/region/state/create/',
]


def test_public_pages(client):
    # These urls are publically accessible and their urls shouldn't change with time.
    for page_url in public_pages:
        response = client.get(page_url)
        assert response.status_code == 200, 'Failed for %s' % page_url
        assert 'Log In' in str(response.content)


def test_staff_pages(client):
    normal_user = f.UserFactory(is_staff=False)
    staff_user = f.UserFactory(is_staff=True)

    for page_url in restricted_pages + staff_pages:
        response = client.get(page_url)
        assert response.status_code == 302, 'Failed for %s' % page_url
        assert '/accounts/login?next=%s' % page_url in response['Location']

        # The page should render find after login
        if page_url in staff_pages:
            client.login(normal_user)
            assert response.status_code == 302, 'Failed for %s' % page_url
            assert '/accounts/login?next=%s' % page_url in response['Location']
            client.logout()

            client.login(staff_user)
            response = client.get(page_url)
            assert response.status_code == 200, 'Failed for %s' % page_url
            assert normal_user.get_full_name() in str(response.content)
            client.logout()
        else:
            client.login(normal_user)
            response = client.get(page_url)
            assert response.status_code == 200, 'Failed for %s' % page_url
            assert normal_user.get_full_name() in str(response.content)
            client.logout()

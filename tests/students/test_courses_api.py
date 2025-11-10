import pytest
from model_bakery import baker
from rest_framework import status
from students.models import Course, Student


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def course_factory():
    def factory(**kwargs):
        return baker.make(Course, **kwargs)
    return factory


@pytest.fixture
def student_factory():
    def factory(**kwargs):
        return baker.make(Student, **kwargs)
    return factory


@pytest.mark.django_db
def test_get_first_course(api_client, course_factory):
    # Arrange
    course = course_factory(name='Test Course')

    # Act
    response = api_client.get(f'/api/v1/courses/{course.id}/')

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == course.id
    assert response.data['name'] == course.name


@pytest.mark.django_db
def test_get_courses_list(api_client, course_factory):
    # Arrange
    courses = course_factory(_quantity=3)

    # Act
    response = api_client.get('/api/v1/courses/')

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 3
    for i, course in enumerate(courses):
        assert response.data[i]['id'] == course.id
        assert response.data[i]['name'] == course.name


@pytest.mark.django_db
def test_filter_courses_by_id(api_client, course_factory):
    # Arrange
    courses = course_factory(_quantity=3)
    target_course = courses[1]

    # Act
    response = api_client.get('/api/v1/courses/',
                              data={'id': target_course.id})

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['id'] == target_course.id
    assert response.data[0]['name'] == target_course.name


@pytest.mark.django_db
def test_filter_courses_by_name(api_client, course_factory):
    # Arrange
    courses = course_factory(_quantity=3)
    target_course = courses[1]

    # Act
    response = api_client.get('/api/v1/courses/',
                              data={'name': target_course.name})

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['id'] == target_course.id
    assert response.data[0]['name'] == target_course.name


@pytest.mark.django_db
def test_create_course(api_client):
    # Arrange
    course_data = {
        'name': 'New Course',
        'students': []
    }

    # Act
    response = api_client.post('/api/v1/courses/',
                               data=course_data, format='json')

    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    assert Course.objects.count() == 1
    assert Course.objects.get().name == 'New Course'


@pytest.mark.django_db
def test_update_course(api_client, course_factory):
    # Arrange
    course = course_factory(name='Old Name')
    update_data = {
        'name': 'Updated Name',
        'students': []
    }

    # Act
    response = api_client.put(f'/api/v1/courses/{course.id}/',
                              data=update_data, format='json')

    # Assert
    assert response.status_code == status.HTTP_200_OK
    course.refresh_from_db()
    assert course.name == 'Updated Name'


@pytest.mark.django_db
def test_delete_course(api_client, course_factory):
    # Arrange
    course = course_factory()

    # Act
    response = api_client.delete(f'/api/v1/courses/{course.id}/')

    # Assert
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Course.objects.count() == 0


@pytest.mark.django_db
def test_course_student_limit_success(api_client, course_factory,
                                      student_factory, settings):
    # Arrange
    settings.MAX_STUDENTS_PER_COURSE = 3
    course = course_factory()
    students = student_factory(_quantity=2)
    course_data = {
        'name': course.name,
        'students': [student.id for student in students]
    }

    # Act
    response = api_client.put(f'/api/v1/courses/{course.id}/',
                              data=course_data, format='json')

    # Assert
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_course_student_limit_exceeded(api_client, course_factory,
                                       student_factory, settings):
    # Arrange
    settings.MAX_STUDENTS_PER_COURSE = 2
    course = course_factory()
    students = student_factory(_quantity=3)

    course_data = {
        'name': course.name,
        'students': [student.id for student in students]
    }

    # Act
    response = api_client.put(f'/api/v1/courses/{course.id}/',
                              data=course_data, format='json')

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.parametrize('student_count,expected_status', [
    (1, status.HTTP_200_OK),
    (2, status.HTTP_200_OK),
    (3, status.HTTP_400_BAD_REQUEST),
    (4, status.HTTP_400_BAD_REQUEST),
])
def test_course_student_limit_parametrized(api_client, course_factory,
                                           student_factory, settings,
                                           student_count, expected_status):
    # Arrange
    settings.MAX_STUDENTS_PER_COURSE = 2
    course = course_factory()
    students = student_factory(_quantity=student_count)

    course_data = {
        'name': course.name,
        'students': [student.id for student in students]
    }

    # Act
    response = api_client.put(f'/api/v1/courses/{course.id}/',
                              data=course_data, format='json')

    # Assert
    assert response.status_code == expected_status

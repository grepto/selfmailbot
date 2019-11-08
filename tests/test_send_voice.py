import pytest


@pytest.fixture
def recognition_result(mocker):
    return mocker.patch('src.recognize.do_recognition')


@pytest.fixture
def send_mail(mocker):
    return mocker.patch('src.celery.send_mail')


@pytest.fixture
def update(update, tg_voice):
    update.message.voice = tg_voice()
    return update


@pytest.fixture(autouse=True)
def user(update, models):
    user = models.get_user_instance(update.message.from_user, 100500)
    user.email = 'mocked@test.org'
    user.save()


def send_short_voice_recognized(bot_app, update, models, send_mail, mocker, voice):
    update.message.voice.duration = 30
    recognition_result.return_value = ['большой', 'зеленый камнеед', 'сидит в', 'пруду']
    bot_app.call('send_voice', update)

    attachment = send_mail.call_args[1]['attachment']
    attachment.seek(0,0)

    assert attachment.read() == voice

    send_mail.assert_called_once_with(
        user_id=update.message.from_user.id,
        to='mocked@test.org',
        subject='Voice: Большой зеленый камнеед...',
        text='большой зеленый камнеед сидит в пруду',
        variables=dict(
            message_id=100800,
            chat_id=update.message.chat_id,
        ),
        attachment=attachment
    )


def send_short_voice_unrecognized(bot_app, update, models, send_mail, mocker, voice):
    update.message.voice.duration = 30
    recognition_result.return_value = []
    bot_app.call('send_voice', update)

    attachment = send_mail.call_args[1]['attachment']
    attachment.seek(0,0)

    assert attachment.read() == voice

    send_mail.assert_called_once_with(
        user_id=update.message.from_user.id,
        to='mocked@test.org',
        subject='Voice note to self',
        text=' ',
        variables=dict(
            message_id=100800,
            chat_id=update.message.chat_id,
        ),
        attachment=attachment
    )


def send_long_voice(bot_app, update, models, send_mail, mocker, voice):
    update.message.voice.duration = 90
    bot_app.call('send_voice', update)

    attachment = send_mail.call_args[1]['attachment']
    attachment.seek(0,0)

    assert attachment.read() == voice

    send_mail.assert_called_once_with(
        user_id=update.message.from_user.id,
        to='mocked@test.org',
        subject='Voice note to self',
        text=' ',
        variables=dict(
            message_id=100800,
            chat_id=update.message.chat_id,
        ),
        attachment=attachment
    )

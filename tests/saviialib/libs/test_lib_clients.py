from unittest.mock import AsyncMock, MagicMock

import pytest

from saviialib.general_types.api.saviia_api_types import (
    FtpClientConfig,
    SharepointConfig,
)
from saviialib.libs.directory_client import DirectoryClient, DirectoryClientArgs
from saviialib.libs.email_client import EmailClient, EmailClientInitArgs, SendEmailArgs
from saviialib.libs.files_client import (
    FilesClient,
    FilesClientInitArgs,
    ReadArgs,
    WriteArgs,
)
from saviialib.libs.ftp_client import (
    FTPClient,
    FtpClientInitArgs,
    FtpListFilesArgs,
    FtpReadFileArgs,
)
from saviialib.libs.log_client import (
    DebugArgs,
    ErrorArgs,
    InfoArgs,
    LogClient,
    LogClientArgs,
    LogStatus,
    WarningArgs,
)
from saviialib.libs.notification_client import (
    DeleteNotificationArgs,
    DeleteReactionArgs,
    FindNotificationArgs,
    NotificationClient,
    NotificationClientInitArgs,
    NotifyArgs,
    ReactArgs,
    UpdateNotificationArgs,
)
from saviialib.libs.schema_validator_client import SchemaValidatorClient
from saviialib.libs.sftp_client import (
    SFTPClient,
    SFTPClientInitArgs,
)
from saviialib.libs.cloud_client import (
    SharepointClient,
    SharepointClientInitArgs,
    SpCreateFolderArgs,
    SpListFilesArgs,
    SpListFoldersArgs,
    SpUploadFileArgs,
)
from saviialib.libs.weather_client import (
    ForecastArgs,
    WeatherClient,
    WeatherClientInitArgs,
    WeatherMetric,
    WeatherQuery,
)


def _ftp_config() -> FtpClientConfig:
    return FtpClientConfig(
        ftp_host="localhost", ftp_port=21, ftp_user="u", ftp_password="p"
    )


def _sharepoint_config() -> SharepointConfig:
    return SharepointConfig(
        sharepoint_client_id="cid",
        sharepoint_client_secret="sec",
        sharepoint_tenant_id="tid",
        sharepoint_tenant_name="tenant",
        sharepoint_site_name="site",
    )


@pytest.mark.parametrize(
    ("module_path", "client_cls", "args", "client_attr", "valid_name"),
    [
        (
            "saviialib.libs.email_client.email_client",
            EmailClient,
            EmailClientInitArgs("smtplib", "a@test.com", "pw"),
            "SmtpLibClient",
            "smtplib",
        ),
        (
            "saviialib.libs.ftp_client.ftp_client",
            FTPClient,
            FtpClientInitArgs(config=_ftp_config(), client_name="aioftp_client"),
            "AioFTPClient",
            "aioftp_client",
        ),
        (
            "saviialib.libs.files_client.files_client",
            FilesClient,
            FilesClientInitArgs(client_name="aiofiles_client"),
            "AioFilesClient",
            "aiofiles_client",
        ),
        (
            "saviialib.libs.directory_client.directory_client",
            DirectoryClient,
            DirectoryClientArgs(client_name="os_client"),
            "OsClient",
            "os_client",
        ),
        (
            "saviialib.libs.sftp_client.sftp_client",
            SFTPClient,
            SFTPClientInitArgs(
                client_name="asyncssh_sftp",
                password="pw",
                username="u",
                ssh_key_path="",
                host="localhost",
                port=22,
            ),
            "AsyncsshSFTPClient",
            "asyncssh_sftp",
        ),
        (
            "saviialib.libs.notification_client.notification_client",
            NotificationClient,
            NotificationClientInitArgs(
                client_name="discord_client", api_key="token", channel_id="ch"
            ),
            "DiscordClient",
            "discord_client",
        ),
        (
            "saviialib.libs.sharepoint_client.sharepoint_client",
            SharepointClient,
            SharepointClientInitArgs(
                config=_sharepoint_config(), client_name="sharepoint_rest_api"
            ),
            "SharepointRestAPI",
            "sharepoint_rest_api",
        ),
        (
            "saviialib.libs.weather_client.weather_client",
            WeatherClient,
            WeatherClientInitArgs(
                client_name="open_meteo", latitude=1.0, longitude=2.0
            ),
            "OpenmeteoClient",
            "open_meteo",
        ),
    ],
)
def test_should_initialize_supported_clients(
    monkeypatch, module_path, client_cls, args, client_attr, valid_name
):
    module = __import__(module_path, fromlist=[client_attr])
    fake_client = MagicMock()
    monkeypatch.setattr(module, client_attr, lambda *_: fake_client)

    client = client_cls(args)

    assert client.client_obj is fake_client
    if hasattr(client, "client_name"):
        assert client.client_name == valid_name


@pytest.mark.parametrize(
    ("client_cls", "args"),
    [
        (EmailClient, EmailClientInitArgs("invalid", "a@test.com", "pw")),
        (FTPClient, FtpClientInitArgs(config=_ftp_config(), client_name="invalid")),
        (FilesClient, FilesClientInitArgs(client_name="invalid")),
        (DirectoryClient, DirectoryClientArgs(client_name="invalid")),
        (
            SFTPClient,
            SFTPClientInitArgs(
                client_name="invalid",
                password="pw",
                username="u",
                ssh_key_path="",
                host="localhost",
                port=22,
            ),
        ),
        (
            NotificationClient,
            NotificationClientInitArgs(
                client_name="invalid", api_key="token", channel_id="ch"
            ),
        ),
        (
            SharepointClient,
            SharepointClientInitArgs(
                config=_sharepoint_config(), client_name="invalid"
            ),
        ),
        (
            WeatherClient,
            WeatherClientInitArgs(client_name="invalid", latitude=1.0, longitude=2.0),
        ),
    ],
)
def test_should_raise_key_error_for_unsupported_clients(client_cls, args):
    with pytest.raises(KeyError):
        client_cls(args)


@pytest.mark.asyncio
async def test_should_delegate_email_send(monkeypatch):
    module = __import__(
        "saviialib.libs.email_client.email_client", fromlist=["SmtpLibClient"]
    )
    fake_client = MagicMock(send_email=AsyncMock(return_value={"status": "sent"}))
    monkeypatch.setattr(module, "SmtpLibClient", lambda *_: fake_client)
    client = EmailClient(EmailClientInitArgs("smtplib", "a@test.com", "pw"))

    result = await client.send_email(
        SendEmailArgs("to@test.com", "subj", "body", "html")
    )

    assert result == {"status": "sent"}
    fake_client.send_email.assert_awaited_once()


@pytest.mark.asyncio
async def test_should_delegate_ftp_calls(monkeypatch):
    module = __import__(
        "saviialib.libs.ftp_client.ftp_client", fromlist=["AioFTPClient"]
    )
    fake = MagicMock(
        list_files=AsyncMock(return_value=[("f.bin", 10)]),
        read_file=AsyncMock(return_value=b"x"),
    )
    monkeypatch.setattr(module, "AioFTPClient", lambda *_: fake)
    client = FTPClient(
        FtpClientInitArgs(config=_ftp_config(), client_name="aioftp_client")
    )

    files = await client.list_files(FtpListFilesArgs(path="/"))
    data = await client.read_file(FtpReadFileArgs(file_path="/f.bin"))

    assert files == [("f.bin", 10)]
    assert data == b"x"


@pytest.mark.asyncio
async def test_should_delegate_files_client_calls(monkeypatch):
    module = __import__(
        "saviialib.libs.files_client.files_client", fromlist=["AioFilesClient"]
    )
    fake = MagicMock(
        read=AsyncMock(return_value="ok"), write=AsyncMock(return_value=None)
    )
    monkeypatch.setattr(module, "AioFilesClient", lambda *_: fake)
    client = FilesClient(FilesClientInitArgs(client_name="aiofiles_client"))

    read_out = await client.read(ReadArgs(file_path="file.txt", mode="r"))
    await client.write(WriteArgs(file_name="file.txt", file_content="v", mode="w"))

    assert read_out == "ok"
    fake.write.assert_awaited_once()


@pytest.mark.asyncio
async def test_should_delegate_directory_client_calls(monkeypatch):
    module = __import__(
        "saviialib.libs.directory_client.directory_client", fromlist=["OsClient"]
    )
    fake = MagicMock(
        join_paths=MagicMock(return_value="a/b"),
        path_exists=AsyncMock(return_value=True),
        listdir=AsyncMock(return_value=["a"]),
        isdir=AsyncMock(return_value=False),
        makedirs=AsyncMock(return_value=None),
        removedirs=AsyncMock(return_value=None),
        remove_file=AsyncMock(return_value=None),
        walk=AsyncMock(return_value=[]),
        touch=AsyncMock(return_value=None),
        relative_path=MagicMock(return_value="rel"),
        get_basename=MagicMock(return_value="x"),
    )
    monkeypatch.setattr(module, "OsClient", lambda *_: fake)
    client = DirectoryClient(DirectoryClientArgs(client_name="os_client"))

    assert client.join_paths("a", "b") == "a/b"
    assert await client.path_exists(".")
    assert await client.listdir(".") == ["a"]
    assert not await client.isdir(".")
    await client.makedirs("a")
    await client.removedirs("a")
    await client.remove_file("f")
    assert await client.walk(".") == []
    await client.touch("f")
    assert client.relative_path("/a/b", "/a") == "rel"
    assert client.get_basename("/a/x") == "x"


@pytest.mark.asyncio
async def test_should_delegate_notification_client_calls(monkeypatch):
    module = __import__(
        "saviialib.libs.notification_client.notification_client",
        fromlist=["DiscordClient"],
    )
    fake = MagicMock(
        connect=AsyncMock(return_value=None),
        close=AsyncMock(return_value=None),
        notify=AsyncMock(return_value={"id": "1"}),
        list_notifications=AsyncMock(return_value=[{"id": "1"}]),
        react=AsyncMock(return_value={}),
        find_notification=AsyncMock(return_value={"id": "1"}),
        update_notification=AsyncMock(return_value={"id": "1"}),
        delete_notification=AsyncMock(return_value=None),
        delete_reaction=AsyncMock(return_value={}),
    )
    monkeypatch.setattr(module, "DiscordClient", lambda *_: fake)
    client = NotificationClient(
        NotificationClientInitArgs(
            client_name="discord_client", api_key="token", channel_id="ch"
        )
    )

    await client.connect()
    await client.close()
    assert await client.notify(NotifyArgs(content="c", embeds=[], files=[])) == {
        "id": "1"
    }
    assert await client.list_notifications() == [{"id": "1"}]
    await client.react(ReactArgs(notification_id="1", emoji="✅"))
    assert await client.find_notification(
        FindNotificationArgs(notification_id="1")
    ) == {"id": "1"}
    await client.update_notification(
        UpdateNotificationArgs(notification_id="1", new_content="n")
    )
    await client.delete_notification(DeleteNotificationArgs(notification_id="1"))
    await client.delete_reaction(DeleteReactionArgs(notification_id="1", emoji="✅"))


@pytest.mark.asyncio
async def test_should_delegate_sharepoint_client_calls(monkeypatch):
    module = __import__(
        "saviialib.libs.sharepoint_client.sharepoint_client",
        fromlist=["SharepointRestAPI"],
    )
    fake = MagicMock(
        __aenter__=AsyncMock(return_value="ctx"),
        __aexit__=AsyncMock(return_value=None),
        list_files=AsyncMock(return_value={"value": []}),
        list_folders=AsyncMock(return_value={"value": []}),
        upload_file=AsyncMock(return_value={"ok": True}),
        create_folder=AsyncMock(return_value={"ok": True}),
        tenant_id="tid",
        tenant_name="tenant",
        site_name="site",
        client_id="cid",
        client_secret="sec",
    )
    monkeypatch.setattr(module, "SharepointRestAPI", lambda *_: fake)
    client = SharepointClient(
        SharepointClientInitArgs(
            config=_sharepoint_config(), client_name="sharepoint_rest_api"
        )
    )

    assert client.tenant_id == "tid"
    assert client.tenant_name == "tenant"
    assert client.site_name == "site"
    assert client.client_id == "cid"
    assert client.client_secret == "sec"
    assert await client.__aenter__() == "ctx"
    await client.__aexit__(None, None, None)
    assert await client.list_files(SpListFilesArgs(folder_relative_url="/x")) == {
        "value": []
    }
    assert await client.list_folders(SpListFoldersArgs(folder_relative_url="/x")) == {
        "value": []
    }
    assert await client.upload_file(
        SpUploadFileArgs(folder_relative_url="/x", file_name="a", file_content=b"x")
    ) == {"ok": True}
    assert await client.create_folder(SpCreateFolderArgs(folder_relative_url="/x")) == {
        "ok": True
    }


@pytest.mark.asyncio
async def test_should_delegate_weather_client_calls(monkeypatch):
    module = __import__(
        "saviialib.libs.weather_client.weather_client", fromlist=["OpenmeteoClient"]
    )
    fake = MagicMock(
        latitude=1.0,
        longitude=2.0,
        connect=AsyncMock(return_value=None),
        close=AsyncMock(return_value=None),
        forecast=AsyncMock(return_value={"precipitation": {}}),
        metrics=MagicMock(return_value={"x": {}}),
    )
    monkeypatch.setattr(module, "OpenmeteoClient", lambda *_: fake)
    client = WeatherClient(
        WeatherClientInitArgs(client_name="open_meteo", latitude=1.0, longitude=2.0)
    )

    assert client.latitude == 1.0
    assert client.longitude == 2.0
    await client.connect()
    await client.close()
    out = await client.forecast(
        ForecastArgs(
            query=WeatherQuery(metric=WeatherMetric.PRECIPITATION),
            start_date="2025-01-01",
            end_date="2025-01-01",
        )
    )
    assert out == {"precipitation": {}}
    assert client.metrics() == {"x": {}}


def test_should_validate_schema_with_schema_validator_client():
    schema = {
        "type": "object",
        "properties": {"name": {"type": "string"}},
        "required": ["name"],
        "additionalProperties": False,
    }
    client = SchemaValidatorClient(schema=schema)

    assert client.validate({"name": "ok"}) is True


def test_should_raise_for_invalid_schema_validator_payload():
    schema = {
        "type": "object",
        "properties": {"name": {"type": "string"}},
        "required": ["name"],
        "additionalProperties": False,
    }
    client = SchemaValidatorClient(schema=schema)

    with pytest.raises(Exception):
        client.validate({"name": 123})


def test_should_initialize_log_client_and_delegate_methods():
    logger = MagicMock()
    client = LogClient(
        LogClientArgs(
            client_name="logging",
            class_name="cls",
            method_name="m",
            active_record=True,
            logger=logger,
        )
    )

    client.method_name = "execute"
    client.info(InfoArgs(LogStatus.STARTED, {"msg": "i"}))
    client.debug(DebugArgs(LogStatus.SUCCESSFUL, {"msg": "d"}))
    client.warning(WarningArgs(LogStatus.ALERT, {"msg": "w"}))
    client.error(ErrorArgs(LogStatus.ERROR, {"msg": "e"}))

    assert client.method_name == "execute"
    assert len(client.log_history) == 4
    logger.info.assert_called_once()
    logger.debug.assert_called_once()
    logger.warning.assert_called_once()
    logger.error.assert_called_once()


def test_should_raise_on_unsupported_log_client():
    with pytest.raises(KeyError):
        LogClient(LogClientArgs(client_name="unknown"))

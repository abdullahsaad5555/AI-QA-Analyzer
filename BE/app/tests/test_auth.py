import re


def extract_otp_from_output(output: str):
    patterns = [
        r"\|\s*OTP:\s*(\d{4,10})",
        r"\bOTP[:=\s]+(\d{4,10})\b",
        r"\botp[:=\s]+(\d{4,10})\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, output, flags=re.IGNORECASE)
        if match:
            return match.group(1)

    fallback = re.findall(r"\b\d{4,10}\b", output)
    return fallback[-1] if fallback else None


def test_send_otp_succeeds(client):
    response = client.post(
        "/api/v1/auth/send-otp",
        json={"email": "test@example.com"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert isinstance(data["message"], str)
    assert data["message"].strip() != ""


def test_send_otp_requires_valid_email(client):
    response = client.post(
        "/api/v1/auth/send-otp",
        json={"email": "not-an-email"},
    )

    assert response.status_code == 422


def test_verify_otp_succeeds(client, capsys):
    email = "verify@example.com"

    send_response = client.post(
        "/api/v1/auth/send-otp",
        json={"email": email},
    )
    assert send_response.status_code == 200

    captured = capsys.readouterr()
    otp = extract_otp_from_output(captured.out + captured.err)

    assert otp is not None
    assert otp.isdigit()

    verify_response = client.post(
        "/api/v1/auth/verify-otp",
        json={
            "email": email,
            "otp": otp,
        },
    )

    assert verify_response.status_code == 200
    data = verify_response.json()

    assert "message" in data
    assert data["message"] == "Login successful"

    assert "tokens" in data
    assert isinstance(data["tokens"], dict)

    assert "access_token" in data["tokens"]
    assert isinstance(data["tokens"]["access_token"], str)
    assert data["tokens"]["access_token"] != ""

    assert "token_type" in data["tokens"]
    assert isinstance(data["tokens"]["token_type"], str)
    assert data["tokens"]["token_type"] != ""

    assert "user" in data
    assert isinstance(data["user"], dict)


def test_verify_otp_rejects_wrong_code(client):
    email = "wrongotp@example.com"

    send_response = client.post(
        "/api/v1/auth/send-otp",
        json={"email": email},
    )
    assert send_response.status_code == 200

    verify_response = client.post(
        "/api/v1/auth/verify-otp",
        json={
            "email": email,
            "otp": "000000",
        },
    )

    assert verify_response.status_code in (400, 401)
    data = verify_response.json()
    assert "detail" in data


def test_verify_otp_requires_fields(client):
    response = client.post(
        "/api/v1/auth/verify-otp",
        json={
            "email": "missingotp@example.com",
        },
    )

    assert response.status_code == 422
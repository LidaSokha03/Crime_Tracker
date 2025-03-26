<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Встановлення паролю</title>
    <link rel="stylesheet" href="registrartion.css">
    <style>
        body {
            background-image: url('red-dark.png');
        }
        
        .form-container {
            max-width: 400px;
            padding: 20px;
        }
        
        .password-instructions {
            color: #666;
            font-size: 12px;
            text-align: center;
            margin-bottom: 15px;
        }
    </style>
</head>
<body>
    <div class="form-container">
        <div class="form-header">
            <h1 class="form-title">SVI.DOC</h1>
        </div>
        
        <div class="form-scrollable">
            <form id="password-form">
                <p class="password-instructions">
                    Введіть надійний пароль. Мінімальна довжина - 8 символів.
                </p>

                <div class="form-group">
                    <label class="form-label">ВВЕДІТЬ ПАРОЛЬ</label>
                    <input type="password" class="form-input" name="password" required minlength="8">
                </div>

                <div class="form-group">
                    <label class="form-label">ПІДТВЕРДІТЬ ПАРОЛЬ</label>
                    <input type="password" class="form-input" name="confirm_password" required minlength="8">
                </div>

                <div class="form-footer">
                    <button type="submit" class="submit-button">ВСТАНОВИТИ ПАРОЛЬ</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        document.getElementById('password-form').addEventListener('submit', function(e) {
            const password = document.querySelector('input[name="password"]').value;
            const confirmPassword = document.querySelector('input[name="confirm_password"]').value;

            if (password !== confirmPassword) {
                e.preventDefault();
                alert('Паролі не збігаються. Спробуйте знову.');
                return;
            }

            if (password.length < 8) {
                e.preventDefault();
                alert('Пароль занадто короткий. Мінімальна довжина - 8 символів.');
                return;
            }
        });
    </script>
</body>
</html>
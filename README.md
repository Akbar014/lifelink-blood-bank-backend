<h1 align="center" id="title">LifeLink Blood Donation Backend ( API )</h1>


<p id="description">This is blood donation website. If anyone is suitable for donating blood then he can register here and donate blood to patient who requested for blood. Donor and receiver both can donate and receive blood. Hope this website able to help many people who need blood urgently. If you are fit for donating blood then please register in our system. Or if you need blood urgently for any emergency patient then please register in our system and create a request for blood donation.</p>

<h2>🚀 Live Demo </h2>

[https://lifelink-five.vercel.app/donate\_blood/](https://lifelink-five.vercel.app/donate_blood/)

  
  
<h2>🧐 Features </h2>

Here're some of the project's best features:

#### User
*   User can register
*   User can login after successfull registration
*   Can create request for donating blood
*   Can create multiple doantion request
*   Can accept blood donation request
*   Check donation history 

<h2>🛠️ Installation Steps:</h2>

<p>1. Clone ripository</p>

```
git clone https://github.com/Akbar014/lifelink-blood-bank-backend.git
```

<p>2. Enter into project directory</p>

```
cd directory_name
```

<p>3. Run comand</p>

```
py manage.py runserver
```
<br>

## 🍰 API Endpoints

- `/auth/register/`
- `/auth/login/`
- `/auth/logout/`

### Donation Endpoints
- `GET /donate_blood/donation-requests/`
- `POST /donate_blood/donation-history/`
- `PUT /donate_blood/donation-accepted/`
- `GET /donate_blood/users/`
- `POST /donate_blood/contactForm/`


  
<h2>💻 Built with</h2>

Technologies used in the project:

*   django
*   django rest framwork
*   postgres
*   cloudinary



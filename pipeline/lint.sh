

function lint(){
  poetry run black ./src
  poetry run isort ./src
  poetry run mypy ./src
  poetry run flake8 ./src --ignore=E501,E203,E704
}
lint
import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    from models.dataset import X_train
    from models.train import model

    return (X_train,)


@app.cell
def _(X_train):
    X_train
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()

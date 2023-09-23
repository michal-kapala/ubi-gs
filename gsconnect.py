from flask import Flask, request, send_from_directory, abort, Response

app = Flask(__name__)

# config for game files directories 
app.config['HOMM5'] = 'D:\\reversing\\homm5\\static\\homm5'
app.config['SP3'] = 'D:\\reversing\\homm5\\static\\sp3'

@app.route('/<php_filename>', methods=['GET'])
def get(php_filename: str) -> Response:
    """The initial request for game server discovery. Returns an `.ini` file with available services."""
    # dp parameter - game key/identifier
    dp = request.args.get('dp')
    game = None
    ini_file = None

    if php_filename=='gsinit.php':
        match dp:
            # Heroes of Might and Magic V
            case 'HEROES_657d2c2ebadc6a1d':
                game = 'HOMM5'
                ini_file = 'servers.ini'
                
            # Tom Clancy’s Splinter Cell: Chaos Theory
            case 'SPLINTERCELL3PS2US':
                game = 'SP3'
                ini_file = 'GS.ini'
                # the game supplies 'user' parameter, e.g. 'noname'
                user = dp = request.args.get('user')

            # Unknown
            case _:
                print('Unknown game id')
                return 'Unknown game id', 400
        try:
            return send_from_directory(directory=app.config[game], path=ini_file, as_attachment=True)
        except FileNotFoundError:
            abort(404)
    else:
        print(f'Unknown request for {php_filename}')
        return 'Unknown request', 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

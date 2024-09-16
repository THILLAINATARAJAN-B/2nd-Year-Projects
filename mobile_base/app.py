

    finally:
        # Close the database connection
        conn.close()
    
    return render_template('setting.html', username=username, user_id=user_id, email=email)



if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0')
